from __future__ import annotations

import pytest

from security import InMemoryRateLimiter, RequestSizeLimitMiddleware


def test_rate_limiter_blocks_after_limit_within_window() -> None:
    limiter = InMemoryRateLimiter(limit=2, window_seconds=60, now=lambda: 100.0)

    assert limiter.check("user-1") is True
    assert limiter.check("user-1") is True
    assert limiter.check("user-1") is False


def test_rate_limiter_resets_after_window() -> None:
    current_time = 100.0
    limiter = InMemoryRateLimiter(limit=1, window_seconds=10, now=lambda: current_time)

    assert limiter.check("user-1") is True
    assert limiter.check("user-1") is False

    current_time = 111.0

    assert limiter.check("user-1") is True


@pytest.mark.asyncio
async def test_request_size_middleware_rejects_large_body() -> None:
    messages = []

    async def app(scope, receive, send):
        message = await receive()
        if message["type"] == "http.disconnect":
            return
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = RequestSizeLimitMiddleware(app, max_body_bytes=3)
    scope = {"type": "http", "method": "POST", "path": "/upload", "headers": []}

    async def receive():
        return {"type": "http.request", "body": b"abcd", "more_body": False}

    async def send(message):
        messages.append(message)

    await middleware(scope, receive, send)

    assert messages[0]["status"] == 413
