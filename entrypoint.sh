#!/bin/bash
python /app/manage.py makemigrations
python /app/manage.py migrate
python /app/manage.py collectstatic --settings=$DJANGO_SETTINGS_MODULE --noinput

exec /usr/local/bin/gunicorn data_facility_enrollment_demo.wsgi \
    --env DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
    --env ENVIRONMENT=local \
    --name data-facility-enrollment-demo \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --log-level info \
    --reload \
    --chdir /app
