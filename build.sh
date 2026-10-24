#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_trustvault_admin
python manage.py check_live_users
python manage.py create_demo_viewers