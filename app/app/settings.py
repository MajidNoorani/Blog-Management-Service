"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from .settings_ckedittor import *
from .settings_jazzmin import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'Verystrongkeyfordjangoblog')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', 1)))

ALLOWED_HOSTS = []
ALLOWED_HOSTS.extend(
    filter(
        None,
        os.environ.get('ALLOWED_HOSTS', '31.214.251.233').split(','),
    )
)

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", 'http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_HEADERS = ['*']
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]
# CSRF_COOKIE_SECURE=False
CSRF_TRUSTED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", 'http://localhost:3000').split(',')

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'core',
    'user',
    'post',
    'django_ckeditor_5',
    'comment',
    'contactUs.contactUs'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'post.middleware.PostViewCountMiddleware'
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'NAME': os.environ.get('DB_NAME', 'BlogDB'),
        'USER': os.environ.get('DB_USER', 'bloguser'),
        'PASSWORD': os.environ.get('DB_PASS', 'verystrongpass2'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Canada/Atlantic'

USE_I18N = False

USE_TZ = True

# Authentication
AUTH_USER_MODEL = 'core.User'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
    ],
    'DEFAULT_PARSER_CLASSES': [
       'rest_framework.parsers.FormParser',
       'rest_framework.parsers.MultiPartParser',
       'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/static/'
MEDIA_URL = 'static/media/'

MEDIA_ROOT = '/vol/web/media'
STATIC_ROOT = '/vol/web/static'
print('BASE_DIR ',BASE_DIR)
STATICFILES_DIRS = [os.path.join(BASE_DIR, STATIC_URL)]
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SPECTACULAR_SETTINGS = {
    # This allows us to upload image through the browsable interface
    'COMPONENT_SPLIT_REQUEST': True,
    'TITLE': 'Blog Management Services',
    'DESCRIPTION': 'All the APIs dedicated to Blog Management service.',
    'VERSION': '1.0.0',
}

LOGIN_REDIRECT_URL = '/'

# Google configuration
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_OAUTH2_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID")
BASE_BACKEND_URL = os.environ.get("BASE_BACKEND_URL", default="http://31.214.251.233:8014")
BASE_FRONTEND_URL = os.environ.get("BASE_FRONTEND_URL", default="http://localhost:3000")


# Email Configuration

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', "mail.example.com")
EMAIL_PORT = os.environ.get('EMAIL_PORT', 465)
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', "mail@example.com")
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', "changeme")
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', "mail@example.com")
EMAIL_SECRET_KEY = os.environ.get('EMAIL_SECRET_KEY', "changeme")


DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000
