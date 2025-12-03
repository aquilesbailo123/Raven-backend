#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
python3 manage.py migrate

# Run wizard.py
python3 wizard.py

# Collect static files for Django
python3 manage.py collectstatic --noinput

# Build command (commented out from original)
# gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT