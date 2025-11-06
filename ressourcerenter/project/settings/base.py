import decimal
import json
import os
import sys
from pathlib import Path
from typing import List


def strtobool(val, return_value_if_nonbool=False):
    if isinstance(val, bool):
        return val
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        if return_value_if_nonbool:
            return val
        raise ValueError("invalid truth value %r" % (val,))


decimal.getcontext().rounding = decimal.ROUND_DOWN

VERSION = os.environ["COMMIT_TAG"]

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = strtobool(os.environ.get("DEBUG", "False"))
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

ALLOWED_HOSTS: List[str] = json.loads(os.environ.get("ALLOWED_HOSTS", "[]"))
CSRF_TRUSTED_ORIGINS = (
    [f"https://{hostname}" for hostname in ALLOWED_HOSTS]
    if ALLOWED_HOSTS != ["*"]
    else []
)

ROOT_URLCONF = "project.urls"

WSGI_APPLICATION = "project.wsgi.application"
ASGI_APPLICATION = "project.asgi.application"

WHITENOISE_USE_FINDERS = True

# Skip health_check for cache layer since we are not using it
WATCHMAN_CHECKS = ("watchman.checks.databases", "watchman.checks.storage")
