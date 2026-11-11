#!/bin/sh
set -eu

# Espera o banco ficar disponível (no Azure o backend pode subir antes do PostgreSQL da VM).
# Só vale para PostgreSQL; com SQLite não há o que esperar.
if [ "${DATABASE_ENGINE:-sqlite}" = "postgresql" ]; then
    python - <<'PY'
import os, sys, time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wedding.settings")
django.setup()
from django.db import connection

limite = int(os.environ.get("DB_WAIT_TIMEOUT", "60"))
inicio = time.time()
while True:
    try:
        connection.ensure_connection()
        print("[entrypoint] banco de dados disponível", flush=True)
        break
    except Exception as exc:
        if time.time() - inicio > limite:
            print(f"[entrypoint] banco indisponível após {limite}s: {exc}", file=sys.stderr, flush=True)
            sys.exit(1)
        print("[entrypoint] aguardando banco de dados...", flush=True)
        time.sleep(2)
PY
fi

if [ "${RUN_COLLECTSTATIC:-true}" = "true" ]; then
    python manage.py collectstatic --noinput
fi

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    python manage.py migrate --noinput
fi

# Cria o superusuário do /admin/ a partir de variáveis (útil no App Service, sem shell):
# DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL e DJANGO_SUPERUSER_PASSWORD.
if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then
    python manage.py createsuperuser --noinput \
        || echo "[entrypoint] superusuário não criado (já existe ou variáveis ausentes)"
fi

exec "$@"
