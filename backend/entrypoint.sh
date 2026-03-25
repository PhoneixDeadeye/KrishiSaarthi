#!/bin/bash
set -e

echo "=== AgriSmart Backend Entrypoint ==="

# Wait for database to be ready
echo "Waiting for database..."
python -c "
import time, os, sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KrishiSaarthi.settings')
django.setup()
from django.db import connections
for i in range(30):
    try:
        connections['default'].cursor()
        print('Database ready!')
        sys.exit(0)
    except Exception:
        print(f'  Waiting... ({i+1}/30)')
        time.sleep(2)
print('ERROR: Database not available after 60s')
sys.exit(1)
"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# Create superuser if env vars set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Ensuring superuser exists..."
    python manage.py createsuperuser --noinput 2>/dev/null || true
fi

echo "=== Starting server ==="
exec "$@"
