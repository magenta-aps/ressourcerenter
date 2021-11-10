from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ressourcerenter/', include('ressourcerenter.urls', namespace='ressourcerenter')),
    path('indberetning/', include('indberetning.urls', namespace='indberetning'))
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
