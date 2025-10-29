import os

import django.conf.locale
from django.utils.translation import gettext_lazy as _

from project.settings.base import BASE_DIR

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
USE_TZ = True
TIME_ZONE = os.environ["TIMEZONE"]
LANGUAGE_CODE = "da"
USE_I18N = True
USE_L10N = True
LANGUAGES = [
    ("da", _("Danish")),
    ("kl", _("Greenlandic")),
]
LANGUAGE_COOKIE_NAME = "Sullissivik.Portal.Lang"
LANGUAGE_COOKIE_DOMAIN = os.environ["LANGUAGE_COOKIE_DOMAIN"]
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
