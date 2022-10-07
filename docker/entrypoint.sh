#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=true}
TEST=${TEST:=false}
SAMPLE_DATA=${SAMPLE_DATA:=false}
CREATE_DUMMY_USERS=${CREATE_DUMMY_USERS:=false}
SKIP_IDP_METADATA=${SKIP_IDP_METADATA:=false}

django-admin makemessages --all
django-admin compilemessages

python manage.py wait_for_db
python manage.py createcachetable

if [ "$SKIP_IDP_METADATA" = false ]; then
  python manage.py update_mitid_idp_metadata
fi
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
  python manage.py create_sample_data
fi
exec "$@"
