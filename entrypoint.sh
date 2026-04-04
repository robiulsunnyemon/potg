#!/bin/bash
set -e

echo "=> Generating Prisma Client..."
prisma generate

echo "=> Syncing Database Schema..."
prisma db push

echo "=> Running Seed Scripts..."
if [ -f "seed_ratings.py" ]; then
    echo "Running Ratings Seed..."
    python seed_ratings.py
fi

if [ -f "activate_admin.py" ]; then
    echo "Running Admin Activation..."
    python activate_admin.py
fi

echo "=> Starting FastAPI Server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
