#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
echo "PostgreSQL user: $POSTGRES_USER"
while ! pg_isready -h postgres -p 5432 -U "$POSTGRES_USER"; do
  sleep 1
done
echo "PostgreSQL started"

# Run database migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI application..."
exec poetry run python main.py
