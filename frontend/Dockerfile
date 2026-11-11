FROM python:3.12-slim AS static-builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN DJANGO_SECRET_KEY=static-build-only-secret DJANGO_DEBUG=False \
    python manage.py collectstatic --noinput

FROM nginx:1.27-alpine
RUN apk add --no-cache gettext
COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=static-builder /app/staticfiles/ /usr/share/nginx/html/static/

# Valores padrão; sobrescreva por variável de ambiente (compose / App Service).
# NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1 faz a imagem oficial exportar NGINX_LOCAL_RESOLVERS
# (servidores DNS do container), usado pelo "resolver" do template.
ENV BACKEND_SCHEME=http \
    BACKEND_HOST=backend \
    BACKEND_PORT=8000 \
    NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/nginx-health || exit 1
