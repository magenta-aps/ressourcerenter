from project.settings.base import TESTING

MIDDLEWARE = [
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
if not TESTING:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

