"""
Django settings for ressourcerenter project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
from distutils.util import strtobool
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = strtobool(os.environ.get('DJANGO_DEBUG', 'False'))

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'administration',
    'indberetning',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'project.middleware.permissions.PermissionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'project.wsgi.application'
ASGI_APPLICATION = 'project.asgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'da-DK'
TIME_ZONE = os.environ['DJANGO_TIMEZONE']
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('da', _('Danish')),
    ('kl', _('Greenlandic')),
]

# URLS for django login/logout used by administrators.
LOGIN_URL = 'administration:login'

LOGOUT_REDIRECT_URL = 'administration:login'
LOGIN_REDIRECT_URL = 'administration:frontpage'
LOGIN_PROVIDER_CLASS = 'indberetning.login.openid.OpenId'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

OPENID = {
    'mock': os.environ.get('LOGIN_MOCK')
}

DAFO = {
    'mock': strtobool(os.environ.get('PITU_MOCK', 'False')),
    'certificate': os.environ.get('PITU_CERTIFICATE'),
    'key': os.environ.get('PITU_KEY'),
    'root_ca': os.environ.get('PITU_ROOT_CA'),
    'uxp_service_cvr': os.environ.get('PITU_UXP_SERVICE_CVR'),
    'uxp_service_cpr': os.environ.get('PITU_UXP_SERVICE_CPR'),
    'uxp_service_owned_by': os.environ.get('PITU_UXP_SERVICE_OWNED_BY'),
    'uxp_client': os.environ.get('PITU_UXP_CLIENT'),
    'url': os.environ.get('PITU_URL'),
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'project/static')
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

WHITENOISE_USE_FINDERS = True
