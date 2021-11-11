from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


urlpatterns = [
    path('djang-admin/', admin.site.urls),
    path('administration/', include('administration.urls', namespace='administration')),
    path('indberetning/', include('indberetning.urls', namespace='indberetning'))
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
