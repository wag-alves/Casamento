#!/bin/sh
set -eu

# Configura o banco SQLite quando esse for o mecanismo selecionado.
if [ "${DATABASE_ENGINE:-sqlite}" = "sqlite" ]; then
    SQLITE_PATH="${SQLITE_PATH:-/home/db.sqlite3}"
    SQLITE_DIRECTORY="$(dirname "$SQLITE_PATH")"

    echo "[entrypoint] preparando diretório SQLite: $SQLITE_DIRECTORY"

    mkdir -p "$SQLITE_DIRECTORY"

    if [ ! -w "$SQLITE_DIRECTORY" ]; then
        echo "[entrypoint] ERRO: diretório SQLite sem permissão de escrita" >&2
        exit 1
    fi

    echo "[entrypoint] SQLite preparado em: $SQLITE_PATH"
fi

# Espera PostgreSQL somente quando esse banco estiver selecionado.
if [ "${DATABASE_ENGINE:-sqlite}" = "postgresql" ]; then
    python - <<'PY'
import os
import sys
import time
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wedding.settings")
django.setup()

from django.db import connection

timeout = int(os.environ.get("DB_WAIT_TIMEOUT", "60"))
start_time = time.time()

while True:
    try:
        connection.ensure_connection()
        print("[entrypoint] banco PostgreSQL disponível", flush=True)
        break
    except Exception as error:
        if time.time() - start_time > timeout:
            print(
                f"[entrypoint] banco indisponível: {error}",
                file=sys.stderr,
                flush=True
            )
            sys.exit(1)

        print("[entrypoint] aguardando PostgreSQL...", flush=True)
        time.sleep(2)
PY
fi

if [ "${RUN_COLLECTSTATIC:-true}" = "true" ]; then
    python manage.py collectstatic --noinput
fi

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    python manage.py migrate --noinput
fi

if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then
    python manage.py createsuperuser --noinput \
        || echo "[entrypoint] superusuário não criado"
fi

exec "$@"