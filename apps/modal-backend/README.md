# Flipbook Modal Backend

Small FastAPI backend for image map overlays.

## Local Run

```powershell
cd "C:\Users\Max  LEC\Documents\flipbook\apps\modal-backend"
python -m pip install -e ".[dev]"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## API

- `GET /health`
- `POST /v1/overlay/map`
  - multipart field `image`: JPEG, PNG, or WebP
  - form field `query`: location name
  - returns `image/jpeg`

## Production Safety

- Keep real secrets in environment variables, never in Git.
- Set `CORS_ORIGINS` to your real frontend domain before public launch.
- Set `NOMINATIM_USER_AGENT` to include a real app/contact string.
- Keep `NOMINATIM_MIN_INTERVAL_SECONDS=1` or slower for the public OpenStreetMap Nominatim service.
- Use a paid geocoding provider or self-host Nominatim when traffic grows.
- Put this app behind HTTPS using Render, Fly.io, Railway, Modal, or another host.

## GitHub Readiness

The root `.gitignore` excludes `.env`, caches, local uploads, virtualenvs, and `.superpowers/`.
Commit `.env.example`, not `.env`.

## Tests

```powershell
cd "C:\Users\Max  LEC\Documents\flipbook"
python -m pytest apps/modal-backend/tests -v
```
