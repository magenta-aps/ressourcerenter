import os

from project.settings.base import BASE_DIR

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "project/static")
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
