#!/bin/sh

echo "Django App Entry Point"

python manage.py migrate

echo "3. Seeding Initial Data..."
PGPASSWORD="$DB_PASSWORD" psql \
  -h "$DB_HOST" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -f /usr/src/setup_initial_data.sql

exec "$@"