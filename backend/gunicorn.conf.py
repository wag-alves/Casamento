"""Configuração do Gunicorn lida de variáveis de ambiente (nada fixo na imagem)."""
import os

bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')
workers = int(os.environ.get('GUNICORN_WORKERS', os.environ.get('WEB_CONCURRENCY', '3')))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '60'))
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
accesslog = '-'   # stdout -> docker logs / Fluxo de log do App Service
errorlog = '-'
