#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=true}
TEST=${TEST:=false}
SAMPLE_DATA=${SAMPLE_DATA:=false}
CREATE_DUMMY_USERS=${CREATE_DUMMY_USERS:=false}
SKIP_IDP_METADATA=${SKIP_IDP_METADATA:=false}
GENERATE_DB_DOCUMENTATION=${GENERATE_DB_DOCUMENTATION:=true}

django-admin makemessages --all --no-obsolete --add-location file
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

if [ "$GENERATE_DB_DOCUMENTATION" = true ]; then
  java -jar /usr/local/share/schemaspy.jar -dp /usr/local/share/postgresql.jar -t pgsql -s public -db $POSTGRES_DB -host $POSTGRES_HOST -u $POSTGRES_USER -p $POSTGRES_PASSWORD -o /app/project/static/media/er_html
  python manage.py graph_models indberetning administration -X Historical* -g -o /app/project/static/media/aalisakkat_models.png
fi

exec "$@"
