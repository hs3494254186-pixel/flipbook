"""SiliconFlow-backed LLM/VLM client (OpenAI-compatible).
Uses DeepSeek-V3 for planning and Qwen2.5-VL for click resolution.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx
from openai import AsyncOpenAI

_CLIENT: AsyncOpenAI | None = None
DEFAULT_TEXT_MODEL = "deepseek-ai/DeepSeek-V3"
DEFAULT_VISION_MODEL = "Qwen/Qwen3-VL-32B-Instruct"
GROUNDING_USER_AGENT = "openflipbook-local/0.1 (real-world-grounding)"

def _get_client() -> AsyncOpenAI:
    global _CLIENT
    if _CLIENT is None:
        api_key = os.environ.get("SILICONFLOW_API_KEY")
        if not api_key:
            raise RuntimeError("SILICONFLOW_API_KEY is not set")
        _CLIENT = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )
    return _CLIENT

@dataclass
class Citation:
    url: str
    title: str | None = None

@dataclass
class PagePlan:
    page_title: str
    prompt: str
    facts: list[str]
    sources: list[Citation]
    subtitle: str | None = None
    main_subject: dict | None = None
    icons: list[dict] | None = None

@dataclass
class ClickResolution:
    subject: str
    style: str
    subject_context: str = ""

@dataclass
class ClickCandidate:
    x_pct: float
    y_pct: float
    subject: str
    style: str
    salience: float

ENTITY_KINDS = ("person", "place", "item", "creature")

FLIPBOOK_VISUAL_STYLE = (
    "Flipbook.page reference style: generated pixels for the content area inside an outer React shell. "
    "The React shell supplies the rounded browser window, address bar, clear button, and share button; "
    "do not draw browser chrome, tabs, address bars, browser buttons, or page controls inside the generated image. "
    "The generated image should be the inner content plate: a warm off-white paper or clean light-gray canvas "
    "with an architectural textbook plate, blueprint, isometric explainer, map inset, cutaway, or labeled diagram "
    "chosen to fit the subject. Use crisp black/charcoal linework, slate-blue rules, muted sage and stone fills, "
    "and occasional soft accent colors. "
    "For real places, preserve the recognizable real-world outline, landmark arrangement, "
    "waterways, islands, coastlines, roads, and building footprint relationships. "
    "Do not simplify lakes, coastlines, campuses, parks, or buildings into generic square, "
    "round, or grid geometry unless that is accurate to reality. "
    "When the subject naturally has practical visitor/customer details, include a "
    "left or right information panel with small structured sections such as Location, "
    "Buying Tickets, Opening Hours, Access Type, Price, What to Expect, Accessibility, "
    "itinerary steps, booking choices, or a compact comparison table. "
    "Use small pixel-rendered text, icons, thin arrows, pointer lines, callout labels, "
    "circled details, section cutaways, zoomed insets, and clear clickable regions. "
    "The page should feel like an interactive "
    "visual browser demo frame: dense enough to explore, clean enough to read, with all labels "
    "and arrows drawn into the image."
)

FLIPBOOK_NEGATIVE_STYLE = (
    "Avoid ancient Chinese aesthetics, gufeng, museum scrolls, fake antique staining, heavy sepia maps, "
    "terracotta-and-ochre palettes, fantasy poster art, cinematic single-scene illustration, "
    "photorealism, glossy 3D, dark backgrounds, cyberpunk neon, glassmorphism, inner browser chrome, "
    "or a pretty unlabeled hero image. Do not omit labels, arrows, tables, icons, or clickable visual regions."
)

FLIPBOOK_IMAGE_STYLE_SUFFIX = (
    ", match the Flipbook.page demo video style: generated pixels for the inner content area of an outer React shell; "
    "do not draw browser chrome, address bars, browser buttons, top controls, or rounded black window borders inside the image. "
    "Use a clean warm off-white paper or light-gray canvas, architectural textbook plate, blueprint, "
    "isometric explanatory drawing, map inset, cutaway, or labeled diagram, "
    "left-side or right-side information panel with ticket prices, opening hours, location, "
    "access notes, booking steps, or other practical table rows only when the subject supports it, "
    "small imperfect pixel text, icons, thin arrows, callout labels, connector lines, "
    "circled details, zoom insets, cutaway views, and multiple "
    "obvious clickable regions. Preserve the recognizable real-world outline and landmark "
    "layout for real places; do not simplify lakes, coastlines, parks, campuses, or buildings "
    "into generic square or round geometry. Keep it light, spatial, diagrammatic, and page-like. "
    "Avoid ancient Chinese, gufeng, fake antique staining, heavy sepia, terracotta, ochre, "
    "cinematic poster art, photorealism, inner browser chrome, and "
    "unlabeled hero scenes."
)

@dataclass
class ExtractedEntity:
    kind: str
    name: str
    appearance: str
    aliases: list[str]
    facts: list[str]
    state: dict[str, Any]
    confidence: float
    bbox: dict[str, float] | None = None

@dataclass
class EntityUpdate:
    match_name: str
    changes: dict[str, Any]
    confidence: float

@dataclass
class EntityExtractionResult:
    added: list[ExtractedEntity]
    updated: list[EntityUpdate]

def _vlm_model_name() -> str:
    return os.environ.get("VISION_MODEL", DEFAULT_VISION_MODEL)


def _vlm_model() -> str:
    return _vlm_model_name()

def _text_model(online: bool = False) -> str:
    return os.environ.get("TEXT_MODEL", DEFAULT_TEXT_MODEL)


def _safe_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _clamp_unit(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(0.0, min(1.0, number))


def _primitive_state(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, Any] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if isinstance(value, str | int | float | bool) or value is None:
            out[key.strip()[:64]] = value
    return out


def _bbox(raw: Any) -> dict[str, float] | None:
    if not isinstance(raw, dict):
        return None
    required = ("x_pct", "y_pct", "w_pct", "h_pct")
    if not all(k in raw for k in required):
        return None
    x = _clamp_unit(raw.get("x_pct"))
    y = _clamp_unit(raw.get("y_pct"))
    w = _clamp_unit(raw.get("w_pct"))
    h = _clamp_unit(raw.get("h_pct"))
    if w <= 0 or h <= 0:
        return None
    return {
        "x_pct": min(x, 1.0 - min(w, 1.0)),
        "y_pct": min(y, 1.0 - min(h, 1.0)),
        "w_pct": min(w, 1.0),
        "h_pct": min(h, 1.0),
    }


def _parse_extraction(raw: str | None) -> EntityExtractionResult:
    parsed = _safe_json(raw)
    added: list[ExtractedEntity] = []
    updated: list[EntityUpdate] = []

    for item in parsed.get("added", []):
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", "")).strip()
        name = str(item.get("name", "")).strip()
        appearance = str(item.get("appearance", "")).strip()
        if kind not in ENTITY_KINDS or not name or not appearance:
            continue
        aliases = [str(a).strip() for a in item.get("aliases", []) if str(a).strip()][:6]
        facts = [str(f).strip() for f in item.get("facts", []) if str(f).strip()][:6]
        added.append(
            ExtractedEntity(
                kind=kind,
                name=name[:80],
                appearance=appearance[:360],
                aliases=aliases,
                facts=facts,
                state=_primitive_state(item.get("state")),
                confidence=_clamp_unit(item.get("confidence"), 0.5),
                bbox=_bbox(item.get("bbox")),
            )
        )

    for item in parsed.get("updated", []):
        if not isinstance(item, dict):
            continue
        match_name = str(item.get("match_name", "")).strip()
        if not match_name:
            continue
        raw_changes = item.get("changes")
        changes: dict[str, Any] = {}
        if isinstance(raw_changes, dict):
            if "appearance" in raw_changes and str(raw_changes["appearance"]).strip():
                changes["appearance"] = str(raw_changes["appearance"]).strip()[:360]
            if "facts" in raw_changes and isinstance(raw_changes["facts"], list):
                changes["facts"] = [
                    str(f).strip() for f in raw_changes["facts"] if str(f).strip()
                ][:6]
            if "state" in raw_changes:
                changes["state"] = _primitive_state(raw_changes["state"])
        updated.append(
            EntityUpdate(
                match_name=match_name[:80],
                changes=changes,
                confidence=_clamp_unit(item.get("confidence"), 0.5),
            )
        )

    return EntityExtractionResult(added=added, updated=updated)


def _format_world_context_clause(world_context: list[dict[str, Any]] | None) -> str:
    if not world_context:
        return ""
    lines: list[str] = []
    for entity in world_context[:16]:
        name = str(entity.get("name", "")).strip()
        appearance = str(entity.get("appearance", "")).strip()
        if not name or not appearance:
            continue
        kind = str(entity.get("kind", "entity")).strip() or "entity"
        aliases = [
            str(a).strip() for a in entity.get("aliases", []) if str(a).strip()
        ][:3]
        state = _primitive_state(entity.get("state"))
        suffix = ""
        if aliases:
            suffix += f"; aliases: {', '.join(aliases)}"
        if state:
            suffix += f"; state: {json.dumps(state, ensure_ascii=False)}"
        lines.append(f"- {kind} {name}: {appearance[:260]}{suffix}")
    if not lines:
        return ""
    return (
        "Preserve recurring entities and causal state exactly. Do not reset opened, "
        "closed, lit, wounded, defeated, or transformed state unless the new page "
        "explicitly changes it.\n" + "\n".join(lines)
    )


def _grounding_language(output_locale: str | None) -> str:
    locale = (output_locale or "").lower()
    return "zh" if locale.startswith("zh") else "en"


def _trim(text: Any, limit: int) -> str:
    if not isinstance(text, str):
        return ""
    return " ".join(text.split())[:limit]


async def _fetch_wikipedia_context(
    client: httpx.AsyncClient, query: str, output_locale: str | None
) -> tuple[str, Citation | None]:
    lang = _grounding_language(output_locale)
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    search = await client.get(
        search_url,
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1,
        },
    )
    search.raise_for_status()
    results = search.json().get("query", {}).get("search", [])
    if not results and lang != "en":
        return await _fetch_wikipedia_context(client, query, "en")
    if not results:
        return "", None

    title = str(results[0].get("title", "")).strip()
    if not title:
        return "", None
    summary_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title, safe='')}"
    summary = await client.get(summary_url)
    summary.raise_for_status()
    data = summary.json()
    extract = _trim(data.get("extract"), 900)
    description = _trim(data.get("description"), 160)
    coordinates = data.get("coordinates") if isinstance(data.get("coordinates"), dict) else {}
    coord_clause = ""
    if "lat" in coordinates and "lon" in coordinates:
        coord_clause = f" Coordinates: {coordinates.get('lat')}, {coordinates.get('lon')}."
    page_url = (
        data.get("content_urls", {})
        .get("desktop", {})
        .get("page")
    )
    bits = [f"Wikipedia title: {title}."]
    if description:
        bits.append(f"Description: {description}.")
    if extract:
        bits.append(f"Summary: {extract}")
    if coord_clause:
        bits.append(coord_clause.strip())
    citation = Citation(url=page_url, title=title) if isinstance(page_url, str) else None
    return " ".join(bits), citation


async def _fetch_osm_context(
    client: httpx.AsyncClient, query: str
) -> tuple[str, Citation | None]:
    response = await client.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "format": "jsonv2",
            "q": query,
            "limit": 1,
            "addressdetails": 1,
            "extratags": 1,
            "namedetails": 1,
        },
    )
    response.raise_for_status()
    results = response.json()
    if not isinstance(results, list) or not results:
        return "", None
    place = results[0]
    if not isinstance(place, dict):
        return "", None
    display_name = _trim(place.get("display_name"), 360)
    place_class = _trim(place.get("class"), 80)
    place_type = _trim(place.get("type"), 80)
    lat = _trim(place.get("lat"), 40)
    lon = _trim(place.get("lon"), 40)
    bbox = place.get("boundingbox")
    bbox_clause = ""
    if isinstance(bbox, list) and len(bbox) == 4:
        bbox_clause = (
            f" bounding box south/north/west/east: {bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}."
        )
    line = (
        "OpenStreetMap/Nominatim result: "
        f"{display_name}; class={place_class}; type={place_type}; "
        f"center={lat},{lon};{bbox_clause}"
    )
    osm_type = _trim(place.get("osm_type"), 24)
    osm_id = _trim(place.get("osm_id"), 32)
    url = None
    if osm_type and osm_id:
        url = f"https://www.openstreetmap.org/{osm_type}/{osm_id}"
    return line, Citation(url=url, title=display_name) if url else None


async def _fetch_real_world_context(
    query: str, output_locale: str | None
) -> tuple[str, list[Citation]]:
    timeout = httpx.Timeout(5.0, connect=3.0)
    headers = {"User-Agent": GROUNDING_USER_AGENT}
    chunks: list[str] = []
    citations: list[Citation] = []
    async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
        for fetcher in (
            lambda: _fetch_wikipedia_context(client, query, output_locale),
            lambda: _fetch_osm_context(client, query),
        ):
            try:
                text, citation = await fetcher()
            except Exception:
                continue
            if text:
                chunks.append(text)
            if citation:
                citations.append(citation)

    if not chunks:
        return "", []
    context = (
        "REAL-WORLD GROUNDING: Use these public reference facts as visual constraints. "
        "Do not invent map geometry, landmark layout, water boundaries, islands, roads, "
        "or building shapes when the references give clues. If details are uncertain, "
        "draw fewer exact claims rather than a fake precise shape.\n"
        + "\n".join(f"- {chunk}" for chunk in chunks)
    )
    return context[:2200], citations[:4]


async def click_to_subject(
    image_data_url: str,
    x_pct: float,
    y_pct: float,
    parent_title: str,
    parent_query: str,
    output_locale: str | None = None,
    user_hint: str | None = None,
) -> ClickResolution:
    client = _get_client()

    # Simple prompt for click resolution
    prompt = (
        f"The user clicked at coordinates ({x_pct}, {y_pct}) on an image titled '{parent_title}'. "
        f"Based on the image, what object or concept did they click on? "
        f"Return a very short phrase (1-3 words) as the subject."
    )

    response = await client.chat.completions.create(
        model=_vlm_model_name(),
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ],
        max_tokens=50
    )

    subject = response.choices[0].message.content.strip()
    return ClickResolution(subject=subject, style="", subject_context="")

async def plan_page(
    query: str,
    web_search: bool,
    style_anchor: str | None = None,
    output_locale: str | None = None,
    parent_title: str | None = None,
    parent_query: str | None = None,
    subject_context: str | None = None,
    world_context: list[dict[str, Any]] | None = None,
) -> PagePlan:
    client = _get_client()

    system_prompt = (
        "You are the visual planner for a Flipbook-style image-is-the-UI spatial canvas. "
        "Each output becomes the inner content of a single generated page. Labels, diagrams, and explanatory text are drawn into the image itself, while the outer React shell supplies the browser window controls.\n\n"
        "GLOBAL VISUAL STYLE LOCK:\n"
        f"{FLIPBOOK_VISUAL_STYLE}\n\n"
        "NEGATIVE STYLE LOCK:\n"
        f"{FLIPBOOK_NEGATIVE_STYLE}\n\n"
        "CONTINUITY RULE:\n"
        "When branching from a parent page, keep line weight, saturation, browser chrome, "
        "address-bar style, label style, and spatial camera consistent with the parent. "
        "The next page should feel like a smooth zoom into the same generated visual browser, "
        "not a new art direction.\n\n"
        "COMPOSITION RULES:\n"
        "1. Favor the Flipbook demo layout inside the content plate: a large illustrated scene, "
        "a subject title, fine divider rules, and a structured left or right information panel only when useful. "
        "Do not draw browser chrome, an address bar, Clear/share buttons, or outer window borders inside the generated image; the web app renders those around it. "
        "For real-world places, attractions, museums, restaurants, events, purchasable products, "
        "or bookable services, the panel is strongly preferred and should include practical rows such as "
        "Location, Buying Tickets, Opening Hours, Access Type, Price, What to Expect, "
        "Accessibility, Dress Code, booking steps, time slots, or totals when relevant.\n"
        "2. For overview pages, place the practical panel on the left like the Notre Dame demo. "
        "For deeper booking/detail pages, a right-side reservation or stepper panel is acceptable. "
        "For abstract topics, concepts, people, mechanisms, science, history, or software ideas, "
        "do not invent ticket prices or opening hours; use an optional facts/specs/process panel "
        "only if it improves clarity.\n"
        "3. Include 6-12 meaningful in-image labels/callouts, thin arrows, connector lines, "
        "small icons, circled details, and map-like or cutaway insets. They must be drawn "
        "inside the image, not represented as DOM UI.\n"
        "4. Use a clean 16:9 white or light warm-gray page with generous margins, balanced "
        "negative space, and one clear visual hierarchy.\n"
        "5. Keep perspective shallow, isometric, and diagrammatic. Avoid cinematic camera "
        "angles, realistic skylines, glossy 3D, or decorative poster art.\n"
        "6. The result should look like a Flipbook page you can click into: every major "
        "region should be a legible drawn object, label, table row, icon, or diagram node.\n"
        "7. Never ask for external browser UI overlays for labels or callouts. The content text "
        "must be generated pixels inside the image, but browser chrome and controls must stay outside in the React shell.\n"
        "8. If output_locale is provided, write page_title, subtitle, annotation labels, facts, and in-image label intent in that language. "
        "If no output_locale is provided, match the user's query language.\n\n"
        "RETURN ONLY JSON:\n"
        "{\n"
        "  \"page_title\": \"...\",\n"
        "  \"subtitle\": \"...\",\n"
        "  \"main_subject\": {\n"
        "    \"name\": \"...\",\n"
        "    \"type\": \"overview|map|cutaway|diagram|table|scene\",\n"
        "    \"annotations\": [{ \"label\": \"...\", \"x\": 50, \"y\": 50 }, ...]\n"
        "  },\n"
        "  \"icons\": [{ \"type\": \"food|landmark|nature|object|place\", \"label\": \"...\" }, ...],\n"
        "  \"facts\": [\"...\", ...],\n"
        "  \"prompt\": \"A Flipbook.page-style generated-pixels inner content plate about [SUBJECT], designed to sit inside an outer React shell browser window, do not draw browser chrome or address bars, clean warm off-white paper or light-gray canvas, architectural textbook plate / blueprint / modern isometric explanatory illustration as appropriate, soft watercolor-like fills, crisp charcoal linework, optional left or right information panel when the subject naturally supports practical rows such as Location, Buying Tickets, Opening Hours, Access Type, Price, What to Expect, Accessibility, booking steps, time slots, or totals; for non-visitor topics use facts/specs/process notes only when helpful, small imperfect pixel text, icons, thin arrows, connector lines, callout labels, circled details, zoom insets, cutaway views, multiple clickable regions. Negative: ancient Chinese, gufeng, fake antique staining, heavy sepia, terracotta, ochre, photorealism, glossy 3D, cinematic poster, inner browser chrome, unlabeled hero image.\"\n"
        "}"
    )

    user_prompt = f"Create a Flipbook.page-style visual browser page plan for: {query}."
    if parent_title:
        user_prompt += f" Branching from: '{parent_title}'."
    grounding_sources: list[Citation] = []
    if web_search:
        user_prompt += (
            " Use real-world reference data. For real places and landmarks, prioritize "
            "recognizable geography, landmark layout, boundaries, roads, waterways, islands, "
            "and building relationships over decorative invention."
        )
        real_world_context, grounding_sources = await _fetch_real_world_context(
            query, output_locale
        )
        if real_world_context:
            if "REAL-WORLD GROUNDING" not in real_world_context:
                real_world_context = (
                    "REAL-WORLD GROUNDING: Use these facts as visual constraints. "
                    "Do not invent map geometry, landmark layout, water boundaries, islands, roads, "
                    "or building shapes when references give clues.\n"
                    f"{real_world_context}"
                )
            user_prompt += f"\n\n{real_world_context}"
    if output_locale:
        user_prompt += f" Output language: {output_locale}."
    if style_anchor:
        user_prompt += f" Preserve this parent visual style exactly: {style_anchor}."
    if subject_context:
        user_prompt += f" Interpret the subject in this parent-page context: {subject_context}."
    world_clause = _format_world_context_clause(world_context)
    if world_clause:
        user_prompt += f"\n\n{world_clause}"

    from obs import log
    log("info", "plan_page.prompt", query=query, user_prompt=user_prompt)

    response = await client.chat.completions.create(
        model=_text_model(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    log("info", "plan_page.result", content=content)
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {}

    return PagePlan(
        page_title=parsed.get("page_title", query),
        prompt=parsed.get("prompt", query),
        facts=parsed.get("facts", []),
        sources=grounding_sources,
        subtitle=parsed.get("subtitle"),
        main_subject=parsed.get("main_subject"),
        icons=parsed.get("icons")
    )

async def rewrite_motion_prompt(**kwargs) -> str: return kwargs.get("page_title", "")
async def polish_edit_instruction(instruction, **kwargs) -> str: return instruction


async def precompute_click_candidates(
    image_data_url: str,
    parent_title: str,
    parent_query: str,
    output_locale: str | None = None,
    max_candidates: int = 8,
) -> list[ClickCandidate]:
    client = _get_client()
    prompt = (
        "Find the most interesting clickable regions in this Flipbook page. "
        "Return ONLY JSON with a candidates array. Each candidate must contain "
        "x_pct, y_pct, subject, style, salience. Percent values are 0-1. "
        f"Return at most {max(1, min(8, max_candidates))} candidates. "
        f"Parent title: {parent_title}. Parent query: {parent_query}."
    )
    if output_locale:
        prompt += f" Subjects should be in {output_locale}."

    response = await client.chat.completions.create(
        model=_vlm_model_name(),
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=700,
    )
    parsed = _safe_json(response.choices[0].message.content)
    raw_candidates = parsed.get("candidates", [])
    out: list[ClickCandidate] = []
    for item in raw_candidates:
        if not isinstance(item, dict):
            continue
        subject = str(item.get("subject", "")).strip()
        if not subject:
            continue
        out.append(
            ClickCandidate(
                x_pct=_clamp_unit(item.get("x_pct"), 0.5),
                y_pct=_clamp_unit(item.get("y_pct"), 0.5),
                subject=subject[:80],
                style=str(item.get("style", "")).strip()[:240],
                salience=_clamp_unit(item.get("salience"), 0.5),
            )
        )
        if len(out) >= max(1, min(8, max_candidates)):
            break
    return out


async def extract_entities(
    image_data_url: str,
    caption: str | None = None,
    scene_description: str | None = None,
    prior_entities: list[dict[str, Any]] | None = None,
) -> EntityExtractionResult:
    client = _get_client()
    prior_clause = _format_world_context_clause(prior_entities)
    prompt = (
        "Extract recurring visual entities from this Flipbook page. Track only "
        "person, place, item, or creature. Return ONLY JSON shaped as "
        '{"added":[{"kind":"person","name":"...","appearance":"...",'
        '"aliases":[],"facts":[],"state":{},"confidence":0.8,'
        '"bbox":{"x_pct":0.1,"y_pct":0.1,"w_pct":0.2,"h_pct":0.2}}],'
        '"updated":[{"match_name":"...","changes":{"appearance":"...",'
        '"facts":[],"state":{}},"confidence":0.8}]}. '
        "Use CANONICAL keys for state such as open, closed, lit, wounded, "
        "defeated, transformed, held, broken, visible."
    )
    if caption:
        prompt += f"\nCaption: {caption}"
    if scene_description:
        prompt += f"\nScene: {scene_description}"
    if prior_clause:
        prompt += f"\nExisting entities:\n{prior_clause}"

    response = await client.chat.completions.create(
        model=_vlm_model_name(),
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=1200,
    )
    return _parse_extraction(response.choices[0].message.content)
