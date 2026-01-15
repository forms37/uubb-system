#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput || true
python manage.py migrate

# Crear superusuario automáticamente (si no existe)
python manage.py createsuperuser --noinput || true
