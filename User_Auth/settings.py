"""
Django settings for User_Auth project.
"""

from datetime import timedelta
from pathlib import Path
import environ
import os
import dj_database_url

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

# Inverse for production-specific logic
IS_PRODUCTION = not DEBUG

# Allowed hosts
if DEBUG:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
else:
    ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Rest
    'rest_framework',

    # CORS
    'corsheaders',

    # Allauth (required)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Social Providers (add as needed)
    'allauth.socialaccount.providers.google',

    # DRF Auth Kit
    'auth_kit',
    'auth_kit.social',  # DRF Auth Kit social integration

    # Documentation
    'drf_spectacular',

    # Mail
    'anymail',

    # My apps
    'accounts',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware'
]

ROOT_URLCONF = 'User_Auth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'User_Auth.wsgi.application'


# Database
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Auth & User
AUTH_USER_MODEL = "accounts.CustomUser"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS settings
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID', default=''),
            'secret': env('GOOGLE_CLIENT_SECRET', default=''),
        }
    },
}


# openapi docs settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Django OAuth Project',
    'DESCRIPTION': 'API documentation with authentication using Google OAuth2.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


# rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'auth_kit.authentication.JWTCookieAuthentication'
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}



# allauth settings
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None


# jwt-auth-kit settings
AUTH_KIT = {
    # Authentication
    'AUTH_TYPE': 'jwt',
    'USE_AUTH_COOKIE': True,
    'SESSION_LOGIN': False,

    # Cookie Security
    'AUTH_COOKIE_SECURE': IS_PRODUCTION,
    'AUTH_COOKIE_HTTPONLY': True,
    'AUTH_COOKIE_SAMESITE':  'None' if IS_PRODUCTION else 'Lax',

    # Redirect all email links to your frontend
    'FRONTEND_BASE_URL': env('FRONTEND_URL', default='http://localhost:3000'),
    'REGISTER_EMAIL_CONFIRM_PATH': '/verify',
    'PASSWORD_RESET_CONFIRM_PATH': '/auth/reset-password',

    # Password reset settings
    'OLD_PASSWORD_FIELD_ENABLED': True,
    'PASSWORD_RESET_PREVENT_ENUMERATION': IS_PRODUCTION,

    # Social Auth
    'SOCIAL_LOGIN_AUTH_TYPE': 'code',
    'SOCIAL_LOGIN_CALLBACK_BASE_URL':  env('CALLBACK', default='http://127.0.0.1:3000/login'),
    'SOCIAL_CONNECT_CALLBACK_BASE_URL': env('CALLBACK', default='http://127.0.0.1:3000/login'),
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# --- EMAIL CONFIGURATION ---
# 1. Check for Resend API Key first (Production)
if env('RESEND_API_KEY', default=None):
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
    ANYMAIL = {
        "RESEND_API_KEY": env('RESEND_API_KEY'),
    }
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@your-verified-domain.com')

# 3. Fallback to Console (Local Dev)
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = 'user_auth@localhost'

