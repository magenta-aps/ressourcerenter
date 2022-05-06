from django.urls import path, include
from indberetning.views import CreateIndberetningCreateView, IndberetningsListView, \
    SelectIndberetningsType, LoginView, LoginCallbackView, Frontpage, \
    LogoutView, LogoutCallback, VirksomhedUpdateView, UpdateIndberetningsView, BilagDownloadView, \
    IndberetningCalculateJsonView, MetadataView
from indberetning.apps import IndberetningConfig
app_name = IndberetningConfig.name

urlpatterns = [
    path('', Frontpage.as_view(), name='frontpage'),
    path('company/<uuid:pk>/edit/', VirksomhedUpdateView.as_view(), name='company-edit'),
    path('list/', IndberetningsListView.as_view(), name='indberetning-list'),
    path('select/', SelectIndberetningsType.as_view(), name='type-select'),
    path('indberetning/calculate', IndberetningCalculateJsonView.as_view(), name='indberetning-calculate'),

    path('indberetning/<uuid:periode>/<int:skema>/create/', CreateIndberetningCreateView.as_view(), name='indberetning-create'),
    path('indberetning/<uuid:pk>/edit/', UpdateIndberetningsView.as_view(), name='indberetning-edit'),
    path('bilag/<uuid:pk>/', BilagDownloadView.as_view(), name='bilag-download'),

    path('login/', LoginView.as_view(), name='login'),
    path('login/callback/', LoginCallbackView.as_view(), name='login-callback'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout/callback/', LogoutCallback.as_view(), name='logout-callback'),
    path('metadata/', MetadataView.as_view(), name='metadata'),
]
