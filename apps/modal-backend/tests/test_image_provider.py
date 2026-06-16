"""Unit tests for the SiliconFlow-backed image provider."""

from __future__ import annotations

import base64

import httpx
import pytest

from providers import image


def test_image_size_for_known_aspects() -> None:
    assert image._image_size_for_aspect("16:9") == "1024x576"
    assert image._image_size_for_aspect("9:16") == "576x1024"
    assert image._image_size_for_aspect("1:1") == "1024x1024"


def test_image_size_unknown_aspect_falls_back_square() -> None:
    assert image._image_size_for_aspect("weird") == "1024x1024"


def test_model_override_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_MODEL", "env/model")
    assert image._image_model("override/model") == "override/model"


def test_image_model_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_MODEL", "Kwai-Kolors/Kolors")
    assert image._image_model(None) == "Kwai-Kolors/Kolors"


def test_build_payload_uses_prompt_model_and_size() -> None:
    payload = image._build_payload("draw a pagoda", "16:9", "custom/model")
    assert payload == {
        "model": "custom/model",
        "prompt": "draw a pagoda",
        "image_size": "1024x576",
        "batch_size": 1,
    }


def test_extract_image_url() -> None:
    out = image._extract_image_bytes_payload({"data": [{"url": "https://example.test/a.jpg"}]})
    assert out == ("url", "https://example.test/a.jpg")


def test_extract_image_base64() -> None:
    b64 = base64.b64encode(b"img").decode("ascii")
    out = image._extract_image_bytes_payload({"data": [{"b64_json": b64}]})
    assert out == ("base64", b64)


def test_extract_image_payload_rejects_missing_data() -> None:
    with pytest.raises(RuntimeError, match="missing image data"):
        image._extract_image_bytes_payload({"data": [{}]})


@pytest.mark.asyncio
async def test_generate_image_requires_siliconflow_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SILICONFLOW_API_KEY"):
        await image.generate_image("prompt", "16:9")


@pytest.mark.asyncio
async def test_generate_image_accepts_base64_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SILICONFLOW_API_KEY", "test-key")
    b64 = base64.b64encode(b"jpeg-bytes").decode("ascii")
    seen: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen["headers"] = request.headers
        seen["json"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"data": [{"b64_json": b64}], "request_id": "req-1"})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        image,
        "_http_client",
        lambda **kwargs: httpx.AsyncClient(transport=transport, **kwargs),
    )

    result = await image.generate_image("draw", "16:9", model_override="model/x")

    assert result.jpeg_bytes == b"jpeg-bytes"
    assert result.mime_type == "image/jpeg"
    assert result.model == "model/x"
    assert result.provider_request_id == "req-1"
    assert seen["headers"]["Authorization"] == "Bearer test-key"


def test_encode_data_url_round_trip() -> None:
    out = image.encode_data_url(b"hello", mime_type="image/png")
    assert out.startswith("data:image/png;base64,")
    assert out.endswith("aGVsbG8=")
