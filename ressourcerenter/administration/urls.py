from administration.apps import AdministrationConfig
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from administration.views import FrontpageView
from administration.views import AfgiftsperiodeCreateView, AfgiftsperiodeListView, SatsTabelUpdateView
app_name = AdministrationConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='administration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('frontpage/', FrontpageView.as_view(), name='frontpage'),
    path('afgiftsperiode/create', AfgiftsperiodeCreateView.as_view(), name='afgiftsperiode-create'),
    path('afgiftsperiode/', AfgiftsperiodeListView.as_view(), name='afgiftsperiode-list'),
    path('afgiftsperiode/<uuid:pk>/satstabel', SatsTabelUpdateView.as_view(), name='afgiftsperiode-satstabel'),
]
