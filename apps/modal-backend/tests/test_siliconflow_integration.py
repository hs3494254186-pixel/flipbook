"""Regression tests for the local SiliconFlow provider swap."""

from __future__ import annotations

import importlib

import pytest

from providers import image, image_edit


@pytest.mark.asyncio
async def test_edit_image_accepts_generate_call_instruction_keyword(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    async def fake_generate_image(
        prompt: str,
        aspect_ratio: str,
        tier: str | None = None,
        model_override: str | None = None,
    ) -> image.GeneratedImage:
        seen.update(
            {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "tier": tier,
                "model_override": model_override,
            }
        )
        return image.GeneratedImage(b"img", "image/jpeg", "model/x", "req")

    monkeypatch.setattr(image_edit, "generate_image", fake_generate_image)

    result = await image_edit.edit_image(
        image_data_url="data:image/jpeg;base64,xx",
        instruction="make it more detailed",
        tier="balanced",
        model_override="model/x",
    )

    assert result.jpeg_bytes == b"img"
    assert seen == {
        "prompt": "make it more detailed",
        "aspect_ratio": "16:9",
        "tier": "balanced",
        "model_override": "model/x",
    }


def test_video_provider_imports_without_fal_helpers_on_image_provider() -> None:
    video = importlib.import_module("providers.video")
    assert hasattr(video, "animate_image")


def test_modal_generate_requires_siliconflow_secret() -> None:
    generate = importlib.import_module("generate")
    assert generate.REQUIRED_SECRET_KEYS == ["SILICONFLOW_API_KEY"]
