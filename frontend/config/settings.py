"""
Django settings for Agentic AI MCP Platform Frontend.
"""

from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY
# =========================================================
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-dev-key-change-in-production'
)

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,agentic-ai-frontend.fly.dev,agentic-ai-backend.fly.dev',
    cast=Csv()
)


# =========================================================
# BACKEND API
# =========================================================
BACKEND_API_URL = config(
    'BACKEND_API_URL',
    default='https://agentic-ai-backend.fly.dev/api'
)


# =========================================================
# PROXY (Fly.io)
# =========================================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True


# =========================================================
# CSRF + SESSION (PRODUCTION SAFE)
# =========================================================
CSRF_TRUSTED_ORIGINS = [
    "https://agentic-ai-frontend.fly.dev",
    "https://agentic-ai-backend.fly.dev",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"


# =========================================================
# CORS (CRITICAL FIX)
# =========================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # local apps
    'core',
    'dashboard',
    'tasks',
    'tools',

    # CORS
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST be first

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "https://agentic-ai-frontend.fly.dev",
    "http://localhost:8000",
]

CORS_ALLOW_CREDENTIALS = True


# =========================================================
# APPLICATIONS
# =========================================================
ROOT_URLCONF = 'config.urls'


# =========================================================
# TEMPLATES
# =========================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# =========================================================
# DATABASE
# =========================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================================================
# PASSWORD VALIDATION
# =========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================================================
# INTERNATIONALIZATION
# =========================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =========================================================
# STATIC
# =========================================================
STATIC_URL = 'static/'


# =========================================================
# DEFAULT AUTO FIELD
# =========================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'