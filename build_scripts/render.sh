#!/usr/bin/env bash
# Exit on error
set -o errexit

# Initial setup
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
python3 manage.py migrate
python3 wizard.py

# mkdir -p staticfiles
python3 manage.py collectstatic

# Build command
# gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT