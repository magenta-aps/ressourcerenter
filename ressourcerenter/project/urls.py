from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("administration/", include("administration.urls", namespace="administration")),
    path("indberetning/", include("indberetning.urls", namespace="indberetning")),
    path("statistik/", include("statistik.urls", namespace="statistik")),
    path("", RedirectView.as_view(permanent=False, url="indberetning/")),
    path("", include("django_mitid_auth.urls", namespace="login")),
    path("_ht/", include("watchman.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

if settings.MITID_TEST_ENABLED:
    urlpatterns.append(
        path("mitid_test/", include("mitid_test.urls", namespace="mitid_test"))
    )
