from django.urls import path
from indberetning.views import CreateInberetningCreateView, CompanySelect, IndberetningsListView, \
    SelectIndberetningsType, CreateIndhandlingsCreateView, LoginView, LoginCallbackView, Frontpage, \
    LogoutView, LogoutCallback
from indberetning.apps import IndberetningConfig

app_name = IndberetningConfig.name

urlpatterns = [
    path('frontpage/', Frontpage.as_view(), name='frontpage'),
    path('company-select/', CompanySelect.as_view(), name='company-select'),
    path('list/', IndberetningsListView.as_view(), name='indberetning-list'),
    path('select/', SelectIndberetningsType.as_view(), name='type-select'),
    path('create/', CreateInberetningCreateView.as_view(), name='indberetning-create'),
    path('indhandling/', CreateIndhandlingsCreateView.as_view(), name='indhandling-create'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/callback/', LoginCallbackView.as_view(), name='login-callback'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout/callback/', LogoutCallback.as_view(), name='logout-callback'),
]
