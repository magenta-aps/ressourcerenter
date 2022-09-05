#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=true}
TEST=${TEST:=false}
SAMPLE_DATA=${SAMPLE_DATA:=false}
CREATE_DUMMY_USERS=${CREATE_DUMMY_USERS:=false}

django-admin makemessages --all
django-admin compilemessages

if [ "$MAKE_MIGRATIONS" = true ] || [ "$MIGRATE" = true ] || [ "$TEST" = true ] || [ "$INITIAL_DATA" = true ] || [ "$SAMPLE_DATA" = true ]; then
  python manage.py wait_for_db
  if [ "$MAKE_MIGRATIONS" = true ]; then
    echo 'generating migrations'
    python manage.py makemigrations indberetning administration
  fi
  if [ "$MIGRATE" = true ]; then
    echo 'running migations'
    python manage.py migrate
  fi
  if [ "$CREATE_DUMMY_USERS" = true ]; then
    echo "Creating dummy users"
    python manage.py create_users
  fi
  if [ "$TEST" = true ]; then
    echo 'running tests!'
    python manage.py test
  fi
  if [ "$SAMPLE_DATA" = true ]; then
    echo "Generating sample data"
    python manage.py create_sample_data 12345678
  fi
fi
exec "$@"
