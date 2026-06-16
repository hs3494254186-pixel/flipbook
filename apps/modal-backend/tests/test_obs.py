import pytest

import obs


@pytest.mark.asyncio
async def test_status_payload_reports_required_secret_state(monkeypatch):
    async def fake_check_provider(_name: str, _url: str) -> bool:
        return True

    monkeypatch.setattr(obs, "_check_provider", fake_check_provider)
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    monkeypatch.delenv("FAL_KEY", raising=False)

    missing = await obs.status_payload("test-service")

    assert missing["secrets"] == {
        "siliconflow_api_key": False,
        "fal_key": False,
    }

    monkeypatch.setenv("SILICONFLOW_API_KEY", "test-siliconflow")
    monkeypatch.setenv("FAL_KEY", "test-fal")

    configured = await obs.status_payload("test-service")

    assert configured["secrets"] == {
        "siliconflow_api_key": True,
        "fal_key": True,
    }
