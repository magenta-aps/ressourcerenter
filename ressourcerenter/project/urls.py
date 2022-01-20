from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.generic import RedirectView


urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('administration/', include('administration.urls', namespace='administration')),
    path('indberetning/', include('indberetning.urls', namespace='indberetning')),
    path('', RedirectView.as_view(permanent=False, url='indberetning/')),
    path('_ht/', include('watchman.urls')),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
