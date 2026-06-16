from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import httpx
from PIL import Image, ImageDraw


@dataclass(frozen=True)
class MapReference:
    display_name: str
    place_class: str
    place_type: str
    lat: float
    lon: float
    bbox: tuple[float, float, float, float]
    geojson: dict[str, Any] | None = None


def parse_nominatim_place(place: dict[str, Any]) -> MapReference | None:
    try:
        bbox_values = place["boundingbox"]
        bbox = tuple(float(value) for value in bbox_values)
        if len(bbox) != 4:
            return None
        return MapReference(
            display_name=str(place["display_name"]),
            place_class=str(place.get("class", "")),
            place_type=str(place.get("type", "")),
            lat=float(place["lat"]),
            lon=float(place["lon"]),
            bbox=bbox,  # type: ignore[arg-type]
            geojson=place.get("geojson"),
        )
    except (KeyError, TypeError, ValueError):
        return None


class NominatimClient:
    def __init__(
        self,
        *,
        base_url: str,
        user_agent: str,
        timeout_seconds: float,
        min_interval_seconds: float,
        cache_seconds: int,
    ) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.min_interval_seconds = min_interval_seconds
        self.cache_seconds = cache_seconds
        self._headers = {"User-Agent": user_agent}
        self._cache: dict[str, tuple[float, MapReference | None]] = {}
        self._lock = threading.Lock()
        self._last_request_at = 0.0

    def search(self, query: str) -> MapReference | None:
        normalized = " ".join(query.split()).lower()
        if not normalized:
            return None

        now = time.monotonic()
        cached = self._cache.get(normalized)
        if cached and now < cached[0]:
            return cached[1]

        with self._lock:
            elapsed = time.monotonic() - self._last_request_at
            if elapsed < self.min_interval_seconds:
                time.sleep(self.min_interval_seconds - elapsed)
            self._last_request_at = time.monotonic()

        response = httpx.get(
            self.base_url,
            params={
                "q": query,
                "format": "jsonv2",
                "polygon_geojson": 1,
                "limit": 1,
            },
            headers=self._headers,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        ref = parse_nominatim_place(data[0]) if data else None
        self._cache[normalized] = (time.monotonic() + self.cache_seconds, ref)
        return ref


def overlay_map_reference(image_bytes: bytes, ref: MapReference) -> bytes:
    with Image.open(BytesIO(image_bytes)) as source:
        image = source.convert("RGB")

    width, height = image.size
    inset_w = max(260, min(360, int(width * 0.34)))
    inset_h = max(180, min(260, int(height * 0.42)))
    margin = max(18, int(min(width, height) * 0.035))
    left = width - inset_w - margin
    top = margin
    right = left + inset_w
    bottom = top + inset_h

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((left, top, right, bottom), radius=12, fill=(248, 250, 252, 235))
    draw.rounded_rectangle((left, top, right, bottom), radius=12, outline=(24, 38, 56, 220), width=3)

    map_area = (left + 14, top + 14, right - 14, bottom - 44)
    draw.rectangle(map_area, fill=(218, 236, 230, 255))
    _draw_boundary(draw, map_area, ref)

    pin_x = (map_area[0] + map_area[2]) // 2
    pin_y = (map_area[1] + map_area[3]) // 2
    draw.ellipse((pin_x - 8, pin_y - 8, pin_x + 8, pin_y + 8), fill=(220, 38, 38, 255))
    draw.ellipse((pin_x - 3, pin_y - 3, pin_x + 3, pin_y + 3), fill=(255, 255, 255, 255))

    label = ref.display_name.split(",", 1)[0][:34]
    draw.text((left + 16, bottom - 34), label, fill=(15, 23, 42, 255))

    out = BytesIO()
    image.save(out, format="JPEG", quality=90, optimize=True)
    return out.getvalue()


def _draw_boundary(
    draw: ImageDraw.ImageDraw,
    map_area: tuple[int, int, int, int],
    ref: MapReference,
) -> None:
    if not ref.geojson:
        draw.line((map_area[0], map_area[3], map_area[2], map_area[1]), fill=(71, 85, 105, 180), width=2)
        return

    polygons = _extract_polygons(ref.geojson)
    for polygon in polygons:
        points = [_project_point(lon, lat, ref.bbox, map_area) for lon, lat in polygon]
        if len(points) > 1:
            draw.polygon(points, fill=(59, 130, 246, 70), outline=(37, 99, 235, 220))


def _extract_polygons(geojson: dict[str, Any]) -> list[list[tuple[float, float]]]:
    geo_type = geojson.get("type")
    coordinates = geojson.get("coordinates")
    if geo_type == "Polygon":
        return [_ring_to_points(coordinates[0])] if coordinates else []
    if geo_type == "MultiPolygon":
        return [_ring_to_points(poly[0]) for poly in coordinates or [] if poly]
    return []


def _ring_to_points(ring: list[list[float]]) -> list[tuple[float, float]]:
    return [(float(point[0]), float(point[1])) for point in ring if len(point) >= 2]


def _project_point(
    lon: float,
    lat: float,
    bbox: tuple[float, float, float, float],
    area: tuple[int, int, int, int],
) -> tuple[int, int]:
    south, north, west, east = bbox
    x_ratio = 0.5 if east == west else (lon - west) / (east - west)
    y_ratio = 0.5 if north == south else (north - lat) / (north - south)
    x = area[0] + int(max(0.0, min(1.0, x_ratio)) * (area[2] - area[0]))
    y = area[1] + int(max(0.0, min(1.0, y_ratio)) * (area[3] - area[1]))
    return x, y
