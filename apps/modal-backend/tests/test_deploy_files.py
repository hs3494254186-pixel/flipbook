from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "apps" / "modal-backend"


def test_requirements_file_includes_runtime_dependencies() -> None:
    requirements = (BACKEND_ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "fastapi" in requirements
    assert "uvicorn" in requirements
    assert "python-multipart" in requirements


def test_render_blueprint_points_to_backend_app() -> None:
    blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "rootDir: apps/modal-backend" in blueprint
    assert "uvicorn main:app" in blueprint
