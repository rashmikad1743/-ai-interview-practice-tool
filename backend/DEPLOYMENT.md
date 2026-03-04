# Deployment Guide (Render / Railway / Fly)

This backend serves templates and frontend pages directly from Django.

## 1) Common environment variables

Set these on your platform:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com,.onrender.com,.up.railway.app,.fly.dev`
- `CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://your-app.onrender.com,https://your-app.up.railway.app,https://your-app.fly.dev`
- `DATABASE_URL=postgres://...`
- `MEDIA_ROOT=/var/data/media` (Render), `/data/media` (Fly), `/app/media` (Railway default)

For Vercel serverless runtime:

- filesystem is ephemeral/read-only for persistent writes; avoid relying on saved media files for generated reports
- this project streams report PDFs directly in response, so no persistent media write is required for downloads

## 2) Static + media

- Static files are served by WhiteNoise after `collectstatic`.
- Media files are written to `MEDIA_ROOT`.
- For production reliability, use a persistent disk/volume:
  - Render: attach a disk and keep `MEDIA_ROOT=/var/data/media`
  - Fly: use volume mounted at `/data` and keep `MEDIA_ROOT=/data/media`
  - Railway: filesystem is typically ephemeral; for durable media use S3/Cloudinary.

## 3) Database

Use managed PostgreSQL and set `DATABASE_URL` from platform DB service.

## 4) Render

- `render.yaml` is included.
- Build command runs install, collectstatic, migrate.
- Start command uses gunicorn.

## Vercel

- `vercel.json` and `api/index.py` are included for serverless Django routing.
- In Vercel project settings add env vars:
  - `SECRET_KEY`
  - `DEBUG=False`
  - `DATABASE_URL=postgres://...`
  - `ALLOWED_HOSTS=.vercel.app`
  - `CSRF_TRUSTED_ORIGINS=https://*.vercel.app`
- Ensure database is a managed PostgreSQL reachable from Vercel.
- Build already runs `collectstatic` via `vercel.json` install command.
- Run migrations once after schema changes from local/CI against production DB:
  - `python manage.py migrate`

## 5) Railway

- `Procfile` and `railway.json` are included.
- Add PostgreSQL plugin and map its connection URL to `DATABASE_URL`.
- Run migrations once after deploy:
  - `python manage.py migrate`

## 6) Fly.io

- `fly.toml` and `Dockerfile` are included.
- Create and attach volume:
  - `fly volumes create media_data --size 1`
- Set secrets:
  - `fly secrets set SECRET_KEY=... DATABASE_URL=... ALLOWED_HOSTS=.fly.dev CSRF_TRUSTED_ORIGINS=https://<app>.fly.dev`
- Deploy:
  - `fly deploy`

## 7) Optional seed data

After first deploy, if needed:

- `python manage.py seed_aptitude_questions`
- `python manage.py seed_coding_questions`
