
"""
Configurações do site "Save the Date - Larissa & Wagner".
Compatível com:
- Desenvolvimento local usando SQLite.
- Docker Compose usando PostgreSQL.
- Azure App Service usando SQLite em caminho configurável.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

try:
    from dotenv import load_dotenv

    load_dotenv()

except ImportError:
    pass


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(nome, padrao):
    """
    Lê uma variável de ambiente booleana.

    Valores considerados verdadeiros:
    1, true, yes, on.
    """
    return (
        os.environ.get(nome, str(padrao))
        .strip()
        .lower()
        in ('1', 'true', 'yes', 'on')
    )


# ============================================================
# SEGURANÇA E DEBUG
# ============================================================

# DEBUG desligado por padrão.
# Para desenvolvimento local, configure DJANGO_DEBUG=True.
DEBUG = env_bool('DJANGO_DEBUG', False)


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = (
            'chave-insegura-so-para-desenvolvimento-troque-em-producao'
        )
    else:
        raise ImproperlyConfigured(
            'Defina DJANGO_SECRET_KEY no ambiente de produção.'
        )


ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'DJANGO_ALLOWED_HOSTS',
        'localhost,127.0.0.1'
    ).split(',')
    if host.strip()
]


CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'DJANGO_CSRF_TRUSTED_ORIGINS',
        ''
    ).split(',')
    if origin.strip()
]


if not DEBUG:
    if not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS:
        raise ImproperlyConfigured(
            'Configure DJANGO_ALLOWED_HOSTS corretamente em produção.'
        )


# ============================================================
# APLICATIVOS INSTALADOS
# ============================================================

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


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================================
# CONFIGURAÇÃO DO PROJETO
# ============================================================

ROOT_URLCONF = 'wedding.urls'

WSGI_APPLICATION = 'wedding.wsgi.application'


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


# ============================================================
# BANCO DE DADOS
# ============================================================

# Modos suportados:
#
# DATABASE_ENGINE=sqlite
# DATABASE_ENGINE=postgresql
#
# Desenvolvimento local:
# SQLite em BASE_DIR/db.sqlite3.
#
# Docker Compose:
# PostgreSQL no serviço chamado "database".
#
# Azure App Service:
# SQLite em /home/data/db.sqlite3.


DATABASE_ENGINE = os.environ.get(
    'DATABASE_ENGINE',
    'sqlite'
).strip().lower()


if DATABASE_ENGINE == 'postgresql':

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',

            'NAME': os.environ.get(
                'POSTGRES_DB',
                'casamento'
            ),

            'USER': os.environ.get(
                'POSTGRES_USER',
                'casamento'
            ),

            'PASSWORD': os.environ.get(
                'POSTGRES_PASSWORD',
                ''
            ),

            'HOST': os.environ.get(
                'POSTGRES_HOST',
                'database'
            ),

            'PORT': os.environ.get(
                'POSTGRES_PORT',
                '5432'
            ),

            'CONN_MAX_AGE': int(
                os.environ.get(
                    'DATABASE_CONN_MAX_AGE',
                    '60'
                )
            ),

            'OPTIONS': {
                'connect_timeout': 5,
            },
        }
    }


elif DATABASE_ENGINE == 'sqlite':

    # Permite escolher o caminho do arquivo SQLite
    # por meio da variável SQLITE_PATH.
    #
    # Se ela não existir, utiliza o caminho padrão:
    # BASE_DIR/db.sqlite3.

    SQLITE_PATH = Path(
        os.environ.get(
            'SQLITE_PATH',
            str(BASE_DIR / 'db.sqlite3')
        )
    )

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',

            'NAME': SQLITE_PATH,

            'OPTIONS': {
                'timeout': 30,
            },
        }
    }


else:

    raise ImproperlyConfigured(
        f'DATABASE_ENGINE inválido: {DATABASE_ENGINE}. '
        'Utilize sqlite ou postgresql.'
    )


# ============================================================
# VALIDAÇÃO DE SENHAS
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        )
    },
]


# ============================================================
# IDIOMA E FUSO HORÁRIO
# ============================================================

LANGUAGE_CODE = os.environ.get(
    'DJANGO_LANGUAGE_CODE',
    'pt-br'
)

TIME_ZONE = os.environ.get(
    'DJANGO_TIME_ZONE',
    'America/Sao_Paulo'
)

USE_I18N = True
USE_TZ = True


# ============================================================
# ARQUIVOS ESTÁTICOS
# ============================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ============================================================
# CONFIGURAÇÃO PADRÃO DOS MODELS
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# CONFIGURAÇÃO DE E-MAIL
# ============================================================

# Desenvolvimento:
# Os e-mails aparecem no terminal.
#
# Produção:
# Os e-mails são enviados pelo SMTP configurado.

if DEBUG:

    EMAIL_BACKEND = (
        'django.core.mail.backends.console.EmailBackend'
    )

else:

    EMAIL_BACKEND = (
        'django.core.mail.backends.smtp.EmailBackend'
    )


EMAIL_HOST = os.environ.get(
    'EMAIL_HOST',
    'smtp.gmail.com'
)

EMAIL_PORT = int(
    os.environ.get(
        'EMAIL_PORT',
        '587'
    )
)

EMAIL_USE_TLS = env_bool(
    'EMAIL_USE_TLS',
    True
)

EMAIL_HOST_USER = os.environ.get(
    'EMAIL_HOST_USER',
    ''
)

EMAIL_HOST_PASSWORD = os.environ.get(
    'EMAIL_HOST_PASSWORD',
    ''
)

DEFAULT_FROM_EMAIL = (
    EMAIL_HOST_USER
    or 'nao-responda@savethedate.com'
)


# E-mail que receberá as confirmações de presença
# e as notificações da lista de presentes.

NOTIFICATION_EMAIL = os.environ.get(
    'NOTIFICATION_EMAIL',
    'wagfalcon@gmail.com'
)


# ============================================================
# CONFIGURAÇÃO DO PIX
# ============================================================

# Chave Pix utilizada para gerar o QR Code.

PIX_KEY = os.environ.get(
    'PIX_KEY',
    '00000000000'
)


PIX_NOME = os.environ.get(
    'PIX_NOME',
    'LARISSA E WAGNER'
)


PIX_CIDADE = os.environ.get(
    'PIX_CIDADE',
    'NATAL'
)


# ============================================================
# PROXY REVERSO: NGINX E AZURE APP SERVICE
# ============================================================

# Informa ao Django que o proxy encaminha o protocolo original
# através do cabeçalho X-Forwarded-Proto.

SECURE_PROXY_SSL_HEADER = (
    'HTTP_X_FORWARDED_PROTO',
    'https'
)


# Utiliza o hostname original encaminhado pelo Nginx.

USE_X_FORWARDED_HOST = True


# Cookies seguros somente quando configurados para HTTPS.
# Por padrão, ficam habilitados quando DEBUG=False.

SECURE_COOKIES = env_bool(
    'DJANGO_SECURE_COOKIES',
    not DEBUG
)


SESSION_COOKIE_SECURE = SECURE_COOKIES

CSRF_COOKIE_SECURE = SECURE_COOKIES


# Segurança dos cookies.

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SAMESITE = 'Lax'


# Configurações adicionais para produção.

if not DEBUG:

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = 'DENY'


# ============================================================
# LOGS
# ============================================================

# Os logs são enviados para stdout/stderr.
# Isso permite consultar os erros pelo Docker e pelo
# Fluxo de log do Azure App Service.

LOG_LEVEL = os.environ.get(
    'DJANGO_LOG_LEVEL',
    'INFO'
).upper()


LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'simples': {
            'format': (
                '%(asctime)s %(levelname)s '
                '%(name)s: %(message)s'
            ),
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simples',
        },
    },

    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
}


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}
