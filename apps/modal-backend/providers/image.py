"""SiliconFlow-backed image generation client.
Uses Flux models via SiliconFlow's OpenAI-compatible image endpoint.
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Any

import httpx

SILICONFLOW_IMAGE_ENDPOINT = "https://api.siliconflow.cn/v1/images/generations"
DEFAULT_IMAGE_MODEL = "Kwai-Kolors/Kolors"

@dataclass
class GeneratedImage:
    jpeg_bytes: bytes
    mime_type: str
    model: str
    provider_request_id: str | None


def _image_size_for_aspect(aspect_ratio: str) -> str:
    sizes = {
        "16:9": "1024x576",
        "9:16": "576x1024",
        "1:1": "1024x1024",
        "4:3": "1024x768",
        "3:4": "768x1024",
    }
    return sizes.get(aspect_ratio, "1024x1024")


def _image_model(model_override: str | None = None) -> str:
    return model_override or os.environ.get("IMAGE_MODEL", DEFAULT_IMAGE_MODEL)


def _build_payload(prompt: str, aspect_ratio: str, model_name: str) -> dict[str, Any]:
    return {
        "model": model_name,
        "prompt": prompt,
        "image_size": _image_size_for_aspect(aspect_ratio),
        "batch_size": 1,
    }


def _extract_image_bytes_payload(data: dict[str, Any]) -> tuple[str, str]:
    items = data.get("data")
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise RuntimeError(f"SiliconFlow response missing image data: {data}")

    first = items[0]
    image_url = first.get("url")
    if isinstance(image_url, str) and image_url:
        return ("url", image_url)

    b64_data = first.get("b64_json")
    if isinstance(b64_data, str) and b64_data:
        return ("base64", b64_data)

    raise RuntimeError(f"SiliconFlow response missing image data: {data}")


def _http_client(**kwargs: Any) -> httpx.AsyncClient:
    return httpx.AsyncClient(**kwargs)


async def generate_image(
    prompt: str,
    aspect_ratio: str,
    tier: str | None = None,
    model_override: str | None = None,
) -> GeneratedImage:
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        raise RuntimeError("SILICONFLOW_API_KEY is not set")

    model_name = _image_model(model_override)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = _build_payload(prompt, aspect_ratio, model_name)

    async with _http_client(timeout=60.0) as client:
        response = await client.post(SILICONFLOW_IMAGE_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    payload_type, payload_value = _extract_image_bytes_payload(data)

    if payload_type == "url":
        async with _http_client() as client:
            img_res = await client.get(payload_value)
            img_res.raise_for_status()
            jpeg_bytes = img_res.content
    else:
        jpeg_bytes = base64.b64decode(payload_value)

    return GeneratedImage(
        jpeg_bytes=jpeg_bytes,
        mime_type="image/jpeg",
        model=model_name,
        provider_request_id=data.get("request_id"),
    )

def encode_data_url(jpeg_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    b64 = base64.b64encode(jpeg_bytes).decode("ascii")
    return f"data:{mime_type};base64,{b64}"
