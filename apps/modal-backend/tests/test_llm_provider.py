"""Unit tests for the SiliconFlow-backed LLM/VLM provider."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from providers import llm


def test_text_model_defaults_to_deepseek() -> None:
    assert llm._text_model() == "deepseek-ai/DeepSeek-V3"


def test_text_model_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEXT_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
    assert llm._text_model() == "deepseek-ai/DeepSeek-V4-Flash"


def test_vlm_model_defaults_to_qwen3() -> None:
    assert llm._vlm_model() == "Qwen/Qwen3-VL-32B-Instruct"


def test_vlm_model_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VISION_MODEL", "Qwen/Qwen2.5-VL-72B-Instruct")
    assert llm._vlm_model() == "Qwen/Qwen2.5-VL-72B-Instruct"


def test_flipbook_style_matches_reference_browser_demo() -> None:
    style = f"{llm.FLIPBOOK_VISUAL_STYLE} {llm.FLIPBOOK_IMAGE_STYLE_SUFFIX}"
    required = [
        "outer React shell",
        "do not draw browser chrome",
        "architectural textbook plate",
        "blueprint",
        "warm off-white paper",
        "left or right information panel",
        "thin arrows",
        "callout labels",
        "isometric",
        "generated pixels",
        "Buying Tickets",
        "Opening Hours",
        "Price",
        "booking steps",
        "recognizable real-world outline",
        "Do not simplify lakes",
    ]
    for phrase in required:
        assert phrase in style


def test_flipbook_style_rejects_old_gufeng_prompting() -> None:
    style = llm.FLIPBOOK_VISUAL_STYLE.lower()
    banned = [
        "ancient",
        "antique",
        "gufeng",
        "古风",
        "terracotta",
        "ochre",
    ]
    for word in banned:
        assert word not in style
    assert "avoid ancient chinese" in llm.FLIPBOOK_IMAGE_STYLE_SUFFIX.lower()
    assert "do not draw browser chrome" in llm.FLIPBOOK_IMAGE_STYLE_SUFFIX.lower()
    assert "avoid" in llm.FLIPBOOK_NEGATIVE_STYLE.lower()


def test_safe_json_strict() -> None:
    assert llm._safe_json('{"a": 1}') == {"a": 1}


def test_safe_json_strips_fence() -> None:
    assert llm._safe_json('```json\n{"a": 2}\n```') == {"a": 2}


def test_safe_json_returns_empty_on_garbage() -> None:
    assert llm._safe_json("not json at all") == {}


def test_extraction_parses_minimal_added_entity() -> None:
    raw = json.dumps(
        {
            "added": [
                {
                    "kind": "person",
                    "name": "Mira",
                    "appearance": "tall keeper in navy coat",
                    "confidence": 0.9,
                }
            ],
            "updated": [],
        }
    )
    out = llm._parse_extraction(raw)
    assert len(out.added) == 1
    assert out.updated == []
    assert out.added[0].name == "Mira"
    assert out.added[0].confidence == 0.9


def test_extraction_drops_unknown_kind() -> None:
    raw = '{"added":[{"kind":"vehicle","name":"Cart","appearance":"wooden"}],"updated":[]}'
    assert llm._parse_extraction(raw).added == []


def test_extraction_filters_state_and_clamps_bbox() -> None:
    raw = json.dumps(
        {
            "added": [
                {
                    "kind": "item",
                    "name": "Lantern",
                    "appearance": "brass lamp",
                    "state": {"lit": True, "junk": [1, 2]},
                    "bbox": {"x_pct": 0.9, "y_pct": 0.8, "w_pct": 0.4, "h_pct": 0.5},
                    "confidence": 2,
                }
            ],
            "updated": [],
        }
    )
    entity = llm._parse_extraction(raw).added[0]
    assert entity.state == {"lit": True}
    assert entity.confidence == 1.0
    assert entity.bbox == {"x_pct": 0.6, "y_pct": 0.5, "w_pct": 0.4, "h_pct": 0.5}


def test_extraction_update_keeps_presence_ping() -> None:
    raw = '{"added":[],"updated":[{"match_name":"Mira","changes":{"junk":true}}]}'
    update = llm._parse_extraction(raw).updated[0]
    assert update.match_name == "Mira"
    assert update.changes == {}


def test_world_context_clause_renders_entities_and_state() -> None:
    out = llm._format_world_context_clause(
        [
            {
                "kind": "person",
                "name": "Mira",
                "aliases": ["keeper", "guide", "third", "ignored"],
                "appearance": "tall lighthouse keeper in navy peacoat",
                "state": {"lantern": "lit", "junk": []},
            }
        ]
    )
    assert "Preserve recurring entities" in out
    assert "person Mira" in out
    assert "aliases: keeper, guide, third" in out
    assert '"lantern": "lit"' in out


@pytest.mark.asyncio
async def test_precompute_click_candidates_parses_vlm_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeCompletions:
        async def create(self, **kwargs):
            content = json.dumps(
                {
                    "candidates": [
                        {
                            "x_pct": 1.5,
                            "y_pct": -1,
                            "subject": "West Lake",
                            "style": "map inset",
                            "salience": 0.8,
                        }
                    ]
                }
            )
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    class FakeClient:
        class Chat:
            completions = FakeCompletions()

        chat = Chat()

    monkeypatch.setattr(llm, "_get_client", lambda: FakeClient())
    out = await llm.precompute_click_candidates(
        "data:image/jpeg;base64,xx", "Hangzhou", "Hangzhou", max_candidates=4
    )
    assert len(out) == 1
    assert out[0].x_pct == 1.0
    assert out[0].y_pct == 0.0
    assert out[0].subject == "West Lake"


@pytest.mark.asyncio
async def test_extract_entities_uses_parser(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeCompletions:
        async def create(self, **kwargs):
            content = '{"added":[{"kind":"place","name":"Gate","appearance":"stone arch"}],"updated":[]}'
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    class FakeClient:
        class Chat:
            completions = FakeCompletions()

        chat = Chat()

    monkeypatch.setattr(llm, "_get_client", lambda: FakeClient())
    out = await llm.extract_entities("data:image/jpeg;base64,xx")
    assert len(out.added) == 1
    assert out.added[0].name == "Gate"


@pytest.mark.asyncio
async def test_plan_page_prompt_does_not_force_history_map_or_gufeng(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    class FakeCompletions:
        async def create(self, **kwargs):
            seen.update(kwargs)
            content = json.dumps(
                {
                    "page_title": "Test",
                    "subtitle": "Sub",
                    "facts": [],
                    "prompt": "plain prompt",
                }
            )
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    class FakeClient:
        class Chat:
            completions = FakeCompletions()

        chat = Chat()

    monkeypatch.setattr(llm, "_get_client", lambda: FakeClient())
    await llm.plan_page("杭州", web_search=False, output_locale="zh-CN")
    messages = seen["messages"]
    combined = json.dumps(messages, ensure_ascii=False)
    assert "visual history map" not in combined
    assert "古风" not in combined
    assert "browser chrome frame and breadcrumb address bar drawn into the image" not in combined
    assert "outer React shell" in combined
    assert "architectural textbook plate" in combined
    assert "avoid ancient chinese" in combined.lower()


@pytest.mark.asyncio
async def test_plan_page_prompt_uses_practical_panels_conditionally(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    class FakeCompletions:
        async def create(self, **kwargs):
            seen.update(kwargs)
            content = json.dumps(
                {
                    "page_title": "Test",
                    "subtitle": "Sub",
                    "facts": [],
                    "prompt": "plain prompt",
                }
            )
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    class FakeClient:
        class Chat:
            completions = FakeCompletions()

        chat = Chat()

    monkeypatch.setattr(llm, "_get_client", lambda: FakeClient())
    await llm.plan_page("Notre Dame tickets", web_search=False, output_locale="en")
    combined = json.dumps(seen["messages"], ensure_ascii=False)
    required = [
        "left or right information panel only when useful",
        "Location",
        "Buying Tickets",
        "Opening Hours",
        "Access Type",
        "Price",
        "What to Expect",
        "booking steps",
        "time slots",
        "do not invent ticket prices or opening hours",
        "optional facts/specs/process panel",
    ]
    for phrase in required:
        assert phrase in combined


@pytest.mark.asyncio
async def test_plan_page_injects_real_world_grounding_when_search_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}
    called: dict[str, object] = {}

    class FakeCompletions:
        async def create(self, **kwargs):
            seen.update(kwargs)
            content = json.dumps(
                {
                    "page_title": "西湖",
                    "subtitle": "现实地理约束",
                    "facts": ["杭州西湖"],
                    "prompt": "draw West Lake with real outline",
                }
            )
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    class FakeClient:
        class Chat:
            completions = FakeCompletions()

        chat = Chat()

    async def fake_context(query: str, output_locale: str | None):
        called["query"] = query
        called["output_locale"] = output_locale
        return (
            "Wikipedia: 西湖 is an irregular freshwater lake in Hangzhou.\n"
            "OpenStreetMap: place type water, bounding box 30.20-30.28 lat, "
            "120.10-120.18 lon; preserve causeways and islands."
        ), [llm.Citation(url="https://example.test/west-lake", title="West Lake")]

    monkeypatch.setattr(llm, "_get_client", lambda: FakeClient())
    monkeypatch.setattr(llm, "_fetch_real_world_context", fake_context)
    out = await llm.plan_page("西湖", web_search=True, output_locale="zh-CN")

    combined = json.dumps(seen["messages"], ensure_ascii=False)
    assert called == {"query": "西湖", "output_locale": "zh-CN"}
    assert "REAL-WORLD GROUNDING" in combined
    assert "irregular freshwater lake" in combined
    assert "preserve causeways and islands" in combined
    assert "Do not invent map geometry" in combined
    assert out.sources[0].url == "https://example.test/west-lake"


@pytest.mark.asyncio
async def test_plan_page_skips_real_world_fetch_when_search_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    class FakeCompletions:
        async def create(self, **kwargs):
            seen.update(kwargs)
            content = json.dumps(
                {
                    "page_title": "Test",
                    "subtitle": "Sub",
                    "facts": [],
                    "prompt": "plain prompt",
                }
            )
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    class FakeClient:
        class Chat:
            completions = FakeCompletions()

        chat = Chat()

    async def fail_context(query: str, output_locale: str | None):
        raise AssertionError("real-world context should not be fetched")

    monkeypatch.setattr(llm, "_get_client", lambda: FakeClient())
    monkeypatch.setattr(llm, "_fetch_real_world_context", fail_context)
    await llm.plan_page("imaginary dashboard", web_search=False, output_locale="en")

    combined = json.dumps(seen["messages"], ensure_ascii=False)
    assert "REAL-WORLD GROUNDING" not in combined
