from __future__ import annotations

from typing import Annotated

from anyio import to_thread
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from config import Settings
from providers.map_overlay import NominatimClient, overlay_map_reference
from security import InMemoryRateLimiter, RequestSizeLimitMiddleware, client_key

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Flipbook Modal Backend", version="0.1.0")
    app.state.settings = settings
    app.state.rate_limiter = InMemoryRateLimiter(
        limit=settings.rate_limit_per_minute,
        window_seconds=60,
    )
    app.state.geocoder = NominatimClient(
        base_url=settings.nominatim_url,
        user_agent=settings.nominatim_user_agent,
        timeout_seconds=settings.nominatim_timeout_seconds,
        min_interval_seconds=settings.nominatim_min_interval_seconds,
        cache_seconds=settings.geocode_cache_seconds,
    )

    app.add_middleware(RequestSizeLimitMiddleware, max_body_bytes=settings.max_image_bytes + 4096)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "modal-backend"}

    @app.get("/")
    def root() -> dict[str, object]:
        return {
            "service": "modal-backend",
            "status": "ok",
            "endpoints": ["/health", "/ready", "/v1/overlay/map"],
        }

    @app.get("/ready")
    def ready(request: Request) -> dict[str, object]:
        geocoder = getattr(request.app.state, "geocoder", None)
        return {
            "status": "ready",
            "checks": {"geocoder": "configured" if geocoder is not None else "missing"},
        }

    @app.post("/v1/overlay/map")
    async def overlay_map(
        request: Request,
        image: Annotated[UploadFile, File()],
        query: Annotated[str, Form(min_length=1, max_length=200)],
        _: None = Depends(_enforce_rate_limit),
    ) -> Response:
        settings = request.app.state.settings
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail="Unsupported image type")

        body = await image.read(settings.max_image_bytes + 1)
        if len(body) > settings.max_image_bytes:
            raise HTTPException(status_code=413, detail="Image is too large")

        try:
            ref = await to_thread.run_sync(request.app.state.geocoder.search, query)
        except Exception as exc:
            raise HTTPException(status_code=502, detail="Map lookup failed") from exc
        if ref is None:
            raise HTTPException(status_code=404, detail="Map reference not found")

        try:
            output = overlay_map_reference(body, ref)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid image") from exc
        return Response(content=output, media_type="image/jpeg")

    return app


def _enforce_rate_limit(request: Request) -> None:
    headers = {key.decode().lower(): value.decode() for key, value in request.scope["headers"]}
    host = request.client.host if request.client else None
    key = client_key(headers, host)
    if not request.app.state.rate_limiter.check(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


app = create_app()
