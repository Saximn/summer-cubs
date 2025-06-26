#!/bin/bash

# Exit on any error
set -e

echo "🔧 Running migrations..."
python manage.py migrate

echo "🌱 Prefilling room data..."
python manage.py prefill_rooms

echo "🚀 Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
 