from __future__ import annotations

from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from config import Settings
from main import create_app
from providers.map_overlay import MapReference


def _image_bytes(fmt: str = "JPEG") -> bytes:
    out = BytesIO()
    Image.new("RGB", (640, 360), "#f4f4f0").save(out, format=fmt)
    return out.getvalue()


class StubGeocoder:
    def search(self, query: str):
        assert query == "West Lake"
        return MapReference(
            display_name="West Lake, Hangzhou",
            place_class="natural",
            place_type="water",
            lat=30.243,
            lon=120.142,
            bbox=(30.20, 30.28, 120.10, 120.18),
            geojson={
                "type": "Polygon",
                "coordinates": [
                    [
                        [120.11, 30.21],
                        [120.17, 30.22],
                        [120.16, 30.27],
                        [120.12, 30.26],
                        [120.11, 30.21],
                    ]
                ],
            },
        )


def test_health_endpoint_reports_ready() -> None:
    app = create_app(Settings(environment="test", cors_origins=["*"]))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "modal-backend"}


def test_overlay_endpoint_rejects_unsupported_file_type() -> None:
    app = create_app(Settings(environment="test", cors_origins=["*"]))
    client = TestClient(app)

    response = client.post(
        "/v1/overlay/map",
        data={"query": "West Lake"},
        files={"image": ("note.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 415


def test_overlay_endpoint_rejects_oversized_upload() -> None:
    app = create_app(
        Settings(environment="test", cors_origins=["*"], max_image_bytes=10)
    )
    client = TestClient(app)

    response = client.post(
        "/v1/overlay/map",
        data={"query": "West Lake"},
        files={"image": ("source.jpg", _image_bytes(), "image/jpeg")},
    )

    assert response.status_code == 413


def test_overlay_endpoint_returns_processed_image() -> None:
    app = create_app(Settings(environment="test", cors_origins=["*"]))
    app.state.geocoder = StubGeocoder()
    client = TestClient(app)

    response = client.post(
        "/v1/overlay/map",
        data={"query": "West Lake"},
        files={"image": ("source.jpg", _image_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content.startswith(b"\xff\xd8")
