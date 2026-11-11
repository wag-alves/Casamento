FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Usuário sem privilégios: o Gunicorn não roda como root
RUN useradd --system --create-home --uid 1000 app

COPY --chown=app:app . .
COPY --chown=app:app backend/gunicorn.conf.py /app/gunicorn.conf.py
COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && mkdir -p /app/staticfiles && chown app:app /app/staticfiles

USER app

ENV GUNICORN_BIND=0.0.0.0:8000
EXPOSE 8000

# Usa o /api/health/ (testa também a conexão com o banco). O Host enviado precisa estar em
# DJANGO_ALLOWED_HOSTS; por padrão é "localhost". O Docker usa isto; o App Service ignora HEALTHCHECK.
HEALTHCHECK --interval=15s --timeout=5s --start-period=40s --retries=5 \
  CMD python -c "import os,urllib.request as u; u.urlopen(u.Request('http://127.0.0.1:%s/api/health/' % os.environ.get('GUNICORN_BIND','0.0.0.0:8000').rsplit(':',1)[1], headers={'Host': os.environ.get('HEALTHCHECK_HOST','localhost')}), timeout=4)" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wedding.wsgi:application"]
