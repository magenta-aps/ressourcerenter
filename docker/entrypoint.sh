#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=false}
TEST=${TEST:=false}
SAMPLE_DATA=${SAMPLE_DATA:=false}

if [ "$MAKE_MIGRATIONS" = true ] || [ "$MIGRATE" = true ] || [ "$TEST" = true ] || "$SAMPLE_DATA" = true; then
  python manage.py wait_for_db
  if [ "$MAKE_MIGRATIONS" = true ]; then
    echo 'generating migrations'
    python manage.py makemigrations
  fi
  if [ "$MIGRATE" = true ]; then
    echo 'running migations'
    python manage.py migrate
  fi
  if [ "$TEST" = true ]; then
    echo 'running tests!'
    python manage.py test
  fi
  if [ "$SAMPLE_DATA" = true ]; then
    echo "Generating sample data"
    python manage.py create_sample_data
  fi
fi
exec "$@"
