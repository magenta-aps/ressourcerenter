from project.settings.base import TESTING

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simple_history",
    "administration",
    "indberetning",
    "statistik",
    "watchman",
    "django_mitid_auth",
    "mitid_test",
    "django_extensions",
    "metrics",
]
if not TESTING:
    INSTALLED_APPS.append("debug_toolbar")
