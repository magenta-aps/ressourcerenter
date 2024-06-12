"""
Django settings for ressourcerenter project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import re
import os
from pathlib import Path
from distutils.util import strtobool
from django.utils.translation import gettext_lazy as _
import django.conf.locale

from django.urls import reverse_lazy
import decimal

from indberetning.utils import populate_dummy_session

# Round towards zero (positives round down, negatives round up)
decimal.getcontext().rounding = decimal.ROUND_DOWN

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = strtobool(os.environ.get("DJANGO_DEBUG", "False"))

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "simple_history",
    "administration",
    "indberetning",
    "statistik",
    "watchman",
    "django_mitid_auth",
    "mitid_test",
    "django_extensions",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "project.middleware.permissions.PermissionMiddleware",
    "django_mitid_auth.middleware.LoginManager",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "django_session_timeout.middleware.SessionTimeoutMiddleware",
    "csp.middleware.CSPMiddleware",
]


if DEBUG:
    import socket

    hostname, foo, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {
                "csp": "csp.templatetags.csp",
            },
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"
ASGI_APPLICATION = "project.asgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
USE_TZ = True
TIME_ZONE = os.environ["DJANGO_TIMEZONE"]
LANGUAGE_CODE = "da"
USE_I18N = True
USE_L10N = True
LANGUAGES = [
    ("da", _("Danish")),
    ("kl", _("Greenlandic")),
]
LANGUAGE_COOKIE_NAME = "Sullissivik.Portal.Lang"
LANGUAGE_COOKIE_DOMAIN = os.environ["DJANGO_LANGUAGE_COOKIE_DOMAIN"]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]
DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = "."
USE_THOUSAND_SEPARATOR = True

# Add custom languages not provided by Django
django.conf.locale.LANG_INFO["kl"] = {
    "bidi": False,
    "code": "kl",
    "name": "Greenlandic",
    "name_local": "Kalaallisut",
}

UPLOAD_PATH = "/uploads"
MEDIA_ROOT = "/srv/media/"
# MEDIA_URL = "/media/"


# Don't limit the number of fields in form submission (e.g. a large number of checkboxes)
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "default_cache",
    },
    "saml": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "saml_cache",
        "TIMEOUT": 7200,
    },
}

# URLS for django login/logout used by administrators.
LOGIN_URL = reverse_lazy("administration:login")
LOGOUT_REDIRECT_URL = "administration:login"
LOGIN_REDIRECT_URL = "administration:postlogin"


# URLS for normal people

# Must match namespace given to django_mitid_auth.urls in project/urls.py
LOGIN_NAMESPACE = "login"
LOGIN_MITID_URL = reverse_lazy("login:login")
LOGIN_PROVIDER_CLASS = os.environ.get("LOGIN_PROVIDER_CLASS") or None
LOGIN_MITID_REDIRECT_URL = reverse_lazy("indberetning:frontpage")
LOGOUT_MITID_REDIRECT_URL = reverse_lazy("indberetning:frontpage")

LOGIN_TIMEOUT_URL = reverse_lazy("indberetning:login-timeout")
LOGIN_REPEATED_URL = reverse_lazy("indberetning:login-repeat")
LOGIN_NO_CPRCVR_URL = reverse_lazy("indberetning:login-no-cvr")
LOGIN_WHITELISTED_URLS = [
    "/favicon.ico",
    LOGIN_URL,
    re.compile("^/administration/"),
    re.compile("^/statistik/"),
    re.compile("^/media/"),
    re.compile("^/i18n/"),
    "/_ht/",
    LOGIN_TIMEOUT_URL,
    LOGIN_REPEATED_URL,
    LOGIN_NO_CPRCVR_URL,
]
MITID_TEST_ENABLED = bool(strtobool(os.environ.get("MITID_TEST_ENABLED", "False")))
SESSION_EXPIRE_SECONDS = int(os.environ.get("SESSION_EXPIRE_SECONDS") or 1800)
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_CALLABLE = "indberetning.utils.session_timed_out"
LOGIN_BYPASS_ENABLED = bool(strtobool(os.environ.get("LOGIN_BYPASS_ENABLED", "False")))
DEFAULT_CVR = os.environ.get("DEFAULT_CVR")
DEFAULT_CPR = None
POPULATE_DUMMY_SESSION = populate_dummy_session

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

DAFO = {
    "mock": strtobool(os.environ.get("PITU_MOCK", "False")),
    "certificate": os.environ.get("PITU_CERTIFICATE"),
    "private_key": os.environ.get("PITU_KEY"),
    "root_ca": os.environ.get("PITU_ROOT_CA"),
    "service_header_cvr": os.environ.get("PITU_UXP_SERVICE_CVR"),
    "client_header": os.environ.get("PITU_UXP_CLIENT"),
    "url": os.environ.get("PITU_URL"),
}


PRISME = {
    "wsdl_file": os.environ.get("PRISME_WSDL", ""),
    "auth": {
        "basic": {
            "username": os.environ.get("PRISME_USERNAME", ""),
            "domain": os.environ.get("PRISME_DOMAIN", ""),
            "password": os.environ.get("PRISME_PASSWORD", ""),
        }
    },
    "proxy": {"socks": os.environ.get("PRISME_SOCKS_PROXY")},
}

PRISME_PUSH = {
    "mock": strtobool(os.environ.get("PRISME_PUSH_MOCK", "false")),
    "host": os.environ.get("PRISME_PUSH_HOST"),
    "port": int(os.environ.get("PRISME_PUSH_PORT") or 22),
    "username": os.environ.get("PRISME_PUSH_USERNAME"),
    "password": os.environ.get("PRISME_PUSH_PASSWORD"),
    "known_hosts": os.environ.get("PRISME_PUSH_KNOWN_HOSTS") or None,
    "dirs": {
        "10q_production": os.environ.get("PRISME_PUSH_DEST_PROD_PATH"),
        "10q_development": os.environ.get("PRISME_PUSH_DEST_TEST_PATH"),
    },
    "destinations_available": {
        "10q_production": strtobool(
            os.environ.get("PRISME_PUSH_DEST_PROD_AVAILABLE", "false")
        ),
        "10q_development": strtobool(
            os.environ.get("PRISME_PUSH_DEST_TEST_AVAILABLE", "true")
        ),
    },
    "fielddata": {
        # System-identificerende streng der kommer på transaktioner i Prisme. Max 4 tegn
        "project_id": os.environ.get("PRISME_PUSH_PROJECT_ID"),
        # Brugernummer der kommer på transaktioner i Prisme. Max 4 tegn
        "user_number": os.environ.get("PRISME_PUSH_USER_NUMBER", "0900"),
        # Betalingsart der kommer på transaktioner i Prisme. Max 3 tegn
        "payment_type": int(os.environ.get("PRISME_PUSH_PAYMENT_TYPE") or 0),
        # Kontonummer der danner bro i Prisme SEL
        "account_number": int(os.environ.get("PRISME_PUSH_ACCOUNT_NUMBER") or 0),
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "project/static")
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

WHITENOISE_USE_FINDERS = True

# Skip health_check for cache layer since we are not using it
WATCHMAN_CHECKS = ("watchman.checks.databases", "watchman.checks.storage")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "gunicorn": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["gunicorn"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["gunicorn"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


SAML = {
    "enabled": bool(strtobool(os.environ.get("SAML_ENABLED", "False"))),
    "debug": 1,
    "entityid": os.environ.get("SAML_SP_ENTITY_ID"),
    "idp_entity_id": os.environ.get("SAML_IDP_ENTITY_ID"),
    "name": os.environ.get("SAML_NAME") or "Aalisakkat",
    "description": os.environ.get("SAML_DESCRIPTION") or "Ressourcenter",
    "verify_ssl_cert": False,
    "metadata_remote": os.environ.get("SAML_IDP_METADATA"),
    "metadata": {"local": ["/var/cache/aalisakkat/idp_metadata.xml"]},  # IdP Metadata
    "service": {
        "sp": {
            "name": os.environ.get("SAML_NAME") or "Aalisakkat",
            "hide_assertion_consumer_service": False,
            "endpoints": {
                "assertion_consumer_service": [
                    (
                        os.environ.get("SAML_SP_LOGIN_CALLBACK_URI"),
                        "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                    )
                ],
                "single_logout_service": [
                    (
                        os.environ.get("SAML_SP_LOGOUT_CALLBACK_URI"),
                        "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    ),
                ],
            },
            "required_attributes": [
                "https://data.gov.dk/model/core/specVersion",
                "https://data.gov.dk/concept/core/nsis/loa",
                "https://data.gov.dk/model/core/eid/professional/orgName",
                "https://data.gov.dk/model/core/eid/fullName",
                "https://data.gov.dk/model/core/eid/professional/cvr",
            ],
            "optional_attributes": [
                "https://data.gov.dk/model/core/eid/cprNumber",
            ],
            "name_id_format": [
                "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
            ],
            "signing_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "authn_requests_signed": True,
            "want_assertions_signed": True,
            "want_response_signed": False,
            "allow_unsolicited": True,
            "logout_responses_signed": True,
        }
    },
    "key_file": os.environ.get("SAML_SP_KEY"),
    "cert_file": os.environ.get("SAML_SP_CERTIFICATE"),
    "encryption_keypairs": [
        {
            "key_file": os.environ.get("SAML_SP_KEY"),
            "cert_file": os.environ.get("SAML_SP_CERTIFICATE"),
        },
    ],
    "xmlsec_binary": "/usr/bin/xmlsec1",
    "delete_tmpfiles": True,
    "organization": {
        "name": [("Aalisakkat", "da")],
        "display_name": ["Aalisakkat"],
        "url": [("https://magenta.dk", "da")],
    },
    "contact_person": [
        {
            "given_name": os.environ["SAML_CONTACT_TECHNICAL_NAME"],
            "email_address": os.environ["SAML_CONTACT_TECHNICAL_EMAIL"],
            "type": "technical",
        },
        {
            "given_name": os.environ["SAML_CONTACT_SUPPORT_NAME"],
            "email_address": os.environ["SAML_CONTACT_SUPPORT_EMAIL"],
            "type": "support",
        },
    ],
    "preferred_binding": {
        "attribute_consuming_service": [
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        ],
        "single_logout_service": [
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        ],
    },
}


def show_toolbar(request):
    return False


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}
