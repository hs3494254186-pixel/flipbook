from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class InMemoryRateLimiter:
    def __init__(
        self,
        *,
        limit: int,
        window_seconds: int,
        now: Callable[[], float] | None = None,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._now = now or time.monotonic
        self._buckets: dict[str, _Bucket] = {}

    def check(self, key: str) -> bool:
        now = self._now()
        bucket = self._buckets.get(key)
        if bucket is None or now >= bucket.reset_at:
            self._buckets[key] = _Bucket(count=1, reset_at=now + self.window_seconds)
            return True
        if bucket.count >= self.limit:
            return False
        bucket.count += 1
        return True


@dataclass
class _Bucket:
    count: int
    reset_at: float


class RequestSizeLimitMiddleware:
    def __init__(self, app: ASGIApp, *, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        total = 0
        rejected = False

        async def limited_receive() -> Message:
            nonlocal total, rejected
            message = await receive()
            if message["type"] != "http.request":
                return message
            total += len(message.get("body", b""))
            if total > self.max_body_bytes:
                rejected = True
                return {"type": "http.disconnect"}
            return message

        async def guarded_send(message: Message) -> None:
            if not rejected:
                await send(message)

        await self.app(scope, limited_receive, guarded_send)
        if rejected:
            await send(
                {
                    "type": "http.response.start",
                    "status": 413,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b'{"detail":"Request body too large"}',
                }
            )


def client_key(headers: dict[str, str], host: str | None) -> str:
    forwarded_for = headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return host or "unknown"
