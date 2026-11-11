"""
Configurações do site "Save the Date - Larissa & Wagner"
"""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(nome, padrao):
    """Lê uma variável de ambiente booleana (true/1/yes/on)."""
    return os.environ.get(nome, str(padrao)).strip().lower() in ('1', 'true', 'yes', 'on')


# DEBUG desligado por padrão: quem esquecer a variável em produção não expõe erros detalhados.
# Para desenvolvimento, defina DJANGO_DEBUG=True no .env.
DEBUG = env_bool('DJANGO_DEBUG', False)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'chave-insegura-so-para-desenvolvimento-troque-em-producao'
    else:
        raise ImproperlyConfigured('Defina DJANGO_SECRET_KEY no ambiente de produção.')

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rsvp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wedding.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wedding.wsgi.application'

# SQLite continua disponível para desenvolvimento sem Docker.
# Quando DATABASE_ENGINE=postgresql, os dados vêm das variáveis POSTGRES_*.
if os.environ.get('DATABASE_ENGINE', 'sqlite').lower() == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'casamento'),
            'USER': os.environ.get('POSTGRES_USER', 'casamento'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'database'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': int(os.environ.get('DATABASE_CONN_MAX_AGE', '60')),
            'OPTIONS': {'connect_timeout': 5},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = os.environ.get('DJANGO_LANGUAGE_CODE', 'pt-br')
TIME_ZONE = os.environ.get('DJANGO_TIME_ZONE', 'America/Sao_Paulo')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Configuração de e-mail (envia notificação a cada confirmação de presença)
# ---------------------------------------------------------------------------
# Em desenvolvimento (DEBUG=True) os e-mails aparecem no terminal, ninguém
# recebe nada de verdade. Para enviar e-mails reais, defina DJANGO_DEBUG=False
# no arquivo .env e preencha EMAIL_HOST_USER / EMAIL_HOST_PASSWORD.
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'nao-responda@savethedate.com'

# E-mail que vai receber as confirmações de presença (RSVP) e da lista de presentes
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', 'wagfalcon@gmail.com')

# ---------------------------------------------------------------------------
# Configuração do Pix (usada para gerar o QR Code de pagamento na lista de presentes)
# ---------------------------------------------------------------------------
# PIX_KEY: a chave Pix de vocês (CPF, e-mail, telefone ou chave aleatória)
# PIX_NOME: nome do titular da chave, como aparece no banco (máx. 25 caracteres, sem acento)
# PIX_CIDADE: cidade do titular da chave (máx. 15 caracteres, sem acento)
PIX_KEY = os.environ.get('PIX_KEY', '00000000000')
PIX_NOME = os.environ.get('PIX_NOME', 'LARISSA E WAGNER')
PIX_CIDADE = os.environ.get('PIX_CIDADE', 'NATAL')

# Configuração de proxy reverso (Nginx / Azure App Service).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
# Cookies "Secure" só funcionam sobre HTTPS. Em produção (DEBUG=False) ficam ligados;
# para testar o modo produção em http://localhost, defina DJANGO_SECURE_COOKIES=False.
SECURE_COOKIES = env_bool('DJANGO_SECURE_COOKIES', not DEBUG)
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Logs em stdout/stderr, para aparecerem em `docker logs` e no "Fluxo de log" do App Service.
# Sem isto, com DEBUG=False o Django não imprime os erros (traceback) de requisições.
LOG_LEVEL = os.environ.get('DJANGO_LOG_LEVEL', 'INFO').upper()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simples': {'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simples'},
    },
    'root': {'handlers': ['console'], 'level': LOG_LEVEL},
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}
