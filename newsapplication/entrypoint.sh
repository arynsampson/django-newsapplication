#!/bin/sh

echo "Waiting for database..."

# Wait until MariaDB is ready
while ! nc -z db 3306; do
  sleep 1
done

echo "Database started"

echo "Making migrations..."
python manage.py makemigrations --noinput

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Starting Django..."
exec python manage.py runserver 0.0.0.0:8000