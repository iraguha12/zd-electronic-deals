#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static assets (Tailwind CSS, images, JS)..."
python manage.py collectstatic --no-input

echo "Applying database migrations..."
python manage.py migrate

echo "Seeding initial catalogue and company settings..."
python manage.py seed_zd_data

echo "Build completed successfully!"
