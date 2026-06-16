from __future__ import annotations

from io import BytesIO

from PIL import Image

from providers import map_overlay


def _blank_jpeg() -> bytes:
    image = Image.new("RGB", (1024, 576), "#f4f4f0")
    out = BytesIO()
    image.save(out, format="JPEG")
    return out.getvalue()


def test_parse_nominatim_place_keeps_geojson_boundary() -> None:
    place = {
        "display_name": "West Lake, Hangzhou, Zhejiang, China",
        "class": "natural",
        "type": "water",
        "lat": "30.243",
        "lon": "120.142",
        "boundingbox": ["30.20", "30.28", "120.10", "120.18"],
        "geojson": {
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
    }

    ref = map_overlay.parse_nominatim_place(place)

    assert ref is not None
    assert ref.display_name.startswith("West Lake")
    assert ref.bbox == (30.20, 30.28, 120.10, 120.18)
    assert ref.geojson["type"] == "Polygon"


def test_overlay_real_map_reference_draws_visible_inset() -> None:
    ref = map_overlay.MapReference(
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

    out = map_overlay.overlay_map_reference(_blank_jpeg(), ref)
    rendered = Image.open(BytesIO(out)).convert("RGB")

    assert rendered.getpixel((690, 58)) != (244, 244, 240)
    assert rendered.getpixel((980, 318)) != (244, 244, 240)
