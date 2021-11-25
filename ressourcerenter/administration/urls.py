from administration.apps import AdministrationConfig
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from administration.views import FrontpageView
from administration.views import AfgiftsperiodeCreateView, AfgiftsperiodeListView, AfgiftsperiodeHistoryView, AfgiftsperiodeSatsTabelUpdateView
from administration.views import SatsTabelElementHistoryView
from administration.views import FiskeArtListView, FiskeArtCreateView, FiskeArtUpdateView, FiskeArtHistoryView
from administration.views import ProduktKategoriListView, ProduktKategoriCreateView, ProduktKategoriUpdateView, ProduktKategoriHistoryView

app_name = AdministrationConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='administration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('frontpage/', FrontpageView.as_view(), name='frontpage'),

    path('afgiftsperiode/', AfgiftsperiodeListView.as_view(), name='afgiftsperiode-list'),
    path('afgiftsperiode/create', AfgiftsperiodeCreateView.as_view(), name='afgiftsperiode-create'),
    path('afgiftsperiode/<uuid:pk>/satstabel', AfgiftsperiodeSatsTabelUpdateView.as_view(), name='afgiftsperiode-satstabel'),
    path('afgiftsperiode/<uuid:pk>/history/', AfgiftsperiodeHistoryView.as_view(), name='afgiftsperiode-history'),
    path('satstabelelement/<int:pk>/history/', SatsTabelElementHistoryView.as_view(), name='satstabelelement-history'),

    path('fiskeart/', FiskeArtListView.as_view(), name='fiskeart-list'),
    path('fiskeart/create', FiskeArtCreateView.as_view(), name='fiskeart-create'),
    path('fiskeart/<uuid:pk>/update', FiskeArtUpdateView.as_view(), name='fiskeart-update'),
    path('fiskeart/<uuid:pk>/history/', FiskeArtHistoryView.as_view(), name='fiskeart-history'),

    path('produktkategori/', ProduktKategoriListView.as_view(), name='produktkategori-list'),
    path('produktkategori/create', ProduktKategoriCreateView.as_view(), name='produktkategori-create'),
    path('produktkategori/<uuid:pk>/update', ProduktKategoriUpdateView.as_view(), name='produktkategori-update'),
    path('produktkategori/<uuid:pk>/history/', ProduktKategoriHistoryView.as_view(), name='produktkategori-history'),
]
