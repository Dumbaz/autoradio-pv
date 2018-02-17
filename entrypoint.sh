#!/bin/bash
set -e

python /tmp/manage.py loaddata /tmp/program/fixtures/*.yaml
python /tmp/manage.py runserver 0.0.0.0:8000

exec "$@"
