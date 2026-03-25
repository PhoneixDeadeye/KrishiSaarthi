# Deployment Guide

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Docker | 24+ | Docker Compose v2 included |
| Domain name | - | For SSL/TLS |
| Google Earth Engine | Service account | For satellite analysis |
| Gemini API Key | - | For AI features |

---

## Environment Setup

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/agrismart.git
cd agrismart
cp backend/.env.example backend/.env
```

### 2. Edit `backend/.env`

```env
# Required
DJANGO_SECRET_KEY=<generate-a-strong-key>
GEMINI_API_KEY=<your-gemini-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL in production)
DATABASE_URL=postgres://agrismart:password@db:5432/agrismart

# Optional
OPENWEATHER_API_KEY=<your-key>
GEE_PROJECT=<your-gee-project>
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Auto-create superuser on first boot
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=<strong-password>
```

> Generate a secret key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

---

## Docker Production Deployment

### Start services

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

The backend `entrypoint.sh` automatically:
1. Waits for the database to become available (up to 60 seconds)
2. Runs database migrations
3. Collects static files
4. Creates a superuser if `DJANGO_SUPERUSER_*` env vars are set

### Verify

```bash
# Check all containers are running
docker-compose -f docker-compose.prod.yml ps

# Check backend health
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

### Services

| Service | Internal Port | Description |
|---------|---------------|-------------|
| frontend | 80 | Nginx serving React SPA |
| backend | 8000 | Django + Gunicorn |
| db | 5432 | PostgreSQL |
| redis | 6379 | Cache + Celery broker |

---

## SSL/TLS Configuration

Edit `nginx/nginx.conf` to add your certificate paths:

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/private/privkey.pem;

    # ... existing proxy config
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

Mount certificates in `docker-compose.prod.yml`:

```yaml
services:
  frontend:
    volumes:
      - /etc/letsencrypt/live/yourdomain.com/fullchain.pem:/etc/ssl/certs/fullchain.pem:ro
      - /etc/letsencrypt/live/yourdomain.com/privkey.pem:/etc/ssl/private/privkey.pem:ro
```

---

## Google Earth Engine Authentication

### Option A: Service Account (recommended for production)

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Mount it into the backend container:

```yaml
services:
  backend:
    volumes:
      - ./gee-service-account.json:/app/gee-key.json:ro
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/gee-key.json
```

### Option B: Interactive setup script

```powershell
# Windows only — run before Docker build
.\setup-ee-auth.ps1
```

---

## Monitoring

The `monitoring/` directory contains pre-configured Prometheus and Grafana:

```bash
# Start monitoring stack alongside the app
docker-compose -f docker-compose.prod.yml -f monitoring/docker-compose.monitoring.yml up -d
```

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

Alert rules are defined in `monitoring/alerts.yml`.

---

## Database Backups

```bash
# Dump database
docker-compose -f docker-compose.prod.yml exec db \
  pg_dump -U agrismart agrismart > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20250101.sql | docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U agrismart agrismart
```

---

## CI/CD

The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs on every push and PR:

| Job | What it does |
|-----|-------------|
| **backend** | Python 3.11, Redis service, Django system checks, pytest |
| **frontend** | Node 20, TypeScript type-check, Vite production build |
| **docker** | Builds both Docker images to validate Dockerfiles |

To deploy on merge to `main`, add a deployment step to the workflow (e.g., SSH deploy, AWS ECS, or DigitalOcean App Platform).

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check `docker-compose logs backend` for migration errors |
| Database connection refused | Ensure `db` service is healthy; entrypoint retries 30 times |
| Static files 404 | Verify `collectstatic` ran (check entrypoint logs) |
| Earth Engine errors | Verify service account credentials are mounted correctly |
| Slow first request | ML models load on first use; subsequent requests are fast |

See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for more common issues.
