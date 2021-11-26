from django.urls import path
from indberetning.views import CreateIndberetningCreateView, CompanySelectView, IndberetningsListView, \
    SelectIndberetningsType, LoginView, LoginCallbackView, Frontpage, \
    LogoutView, LogoutCallback, VirksomhedUpdateView, UpdateIndberetningsView, BilagDownloadView
from indberetning.apps import IndberetningConfig
app_name = IndberetningConfig.name

urlpatterns = [
    path('frontpage/', Frontpage.as_view(), name='frontpage'),
    path('company/select/', CompanySelectView.as_view(), name='company-select'),
    path('company/<uuid:pk>/edit/', VirksomhedUpdateView.as_view(), name='company-edit'),
    path('list/', IndberetningsListView.as_view(), name='indberetning-list'),
    path('select/', SelectIndberetningsType.as_view(), name='type-select'),
    path('indberetning/<uuid:pk>/create/', CreateIndberetningCreateView.as_view(), name='indberetning-create'),
    path('indberetning/<uuid:pk>/edit/', UpdateIndberetningsView.as_view(), name='indberetning-edit'),
    path('bilag/<uuid:pk>/', BilagDownloadView.as_view(), name='bilag-download'),

    path('login/', LoginView.as_view(), name='login'),
    path('login/callback/', LoginCallbackView.as_view(), name='login-callback'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout/callback/', LogoutCallback.as_view(), name='logout-callback'),
]
