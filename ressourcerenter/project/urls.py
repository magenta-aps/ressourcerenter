from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.generic import RedirectView
from django.conf.urls.static import static


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("administration/", include("administration.urls", namespace="administration")),
    path("indberetning/", include("indberetning.urls", namespace="indberetning")),
    path("statistik/", include("statistik.urls", namespace="statistik")),
    path("", RedirectView.as_view(permanent=False, url="indberetning/")),
    path("_ht/", include("watchman.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
