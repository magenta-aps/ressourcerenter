from administration.apps import AdministrationConfig
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from administration.views import FrontpageView
from administration.views import AfgiftsperiodeCreateView, AfgiftsperiodeUpdateView, AfgiftsperiodeListView, AfgiftsperiodeHistoryView, AfgiftsperiodeSatsTabelUpdateView
from administration.views import SatsTabelElementHistoryView
from administration.views import FiskeArtListView, FiskeArtCreateView, FiskeArtUpdateView, FiskeArtHistoryView
from administration.views import ProduktTypeListView, ProduktTypeCreateView, ProduktTypeUpdateView, ProduktTypeHistoryView
from administration.views import IndberetningDetailView, IndberetningListView, IndberetningAfstemFormView
from administration.views import VirksomhedListView, VirksomhedCreateView, VirksomhedUpdateView, VirksomhedRepræsentantView, VirksomhedRepræsentantStopView

app_name = AdministrationConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='administration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('frontpage/', FrontpageView.as_view(), name='frontpage'),

    path('afgiftsperiode/', AfgiftsperiodeListView.as_view(), name='afgiftsperiode-list'),
    path('afgiftsperiode/create', AfgiftsperiodeCreateView.as_view(), name='afgiftsperiode-create'),
    path('afgiftsperiode/<uuid:pk>/update', AfgiftsperiodeUpdateView.as_view(), name='afgiftsperiode-update'),
    path('afgiftsperiode/<uuid:pk>/satstabel', AfgiftsperiodeSatsTabelUpdateView.as_view(), name='afgiftsperiode-satstabel'),
    path('afgiftsperiode/<uuid:pk>/history/', AfgiftsperiodeHistoryView.as_view(), name='afgiftsperiode-history'),
    path('satstabelelement/<int:pk>/history/', SatsTabelElementHistoryView.as_view(), name='satstabelelement-history'),

    path('fiskeart/', FiskeArtListView.as_view(), name='fiskeart-list'),
    path('fiskeart/create', FiskeArtCreateView.as_view(), name='fiskeart-create'),
    path('fiskeart/<uuid:pk>/update', FiskeArtUpdateView.as_view(), name='fiskeart-update'),
    path('fiskeart/<uuid:pk>/history/', FiskeArtHistoryView.as_view(), name='fiskeart-history'),

    path('produkttype/', ProduktTypeListView.as_view(), name='produkttype-list'),
    path('produkttype/create', ProduktTypeCreateView.as_view(), name='produkttype-create'),
    path('produkttype/<uuid:pk>/update', ProduktTypeUpdateView.as_view(), name='produkttype-update'),
    path('produkttype/<uuid:pk>/history/', ProduktTypeHistoryView.as_view(), name='produkttype-history'),

    path('indberetning/', IndberetningListView.as_view(), name='indberetning-list'),
    path('indberetning/<uuid:pk>/', IndberetningDetailView.as_view(), name='indberetning-detail'),
    path('indberetning/<uuid:pk>/afstem', IndberetningAfstemFormView.as_view(), name='indberetning-afstem'),

    path('virksomhed/', VirksomhedListView.as_view(), name='virksomhed-list'),
    path('virksomhed/create', VirksomhedCreateView.as_view(), name='virksomhed-create'),
    path('virksomhed/<uuid:pk>/', VirksomhedUpdateView.as_view(), name='virksomhed-update'),
    path('virksomhed/repræsenter/stop/', VirksomhedRepræsentantStopView.as_view(), name='virksomhed-represent-stop'),
    path('virksomhed/<uuid:pk>/repræsenter/', VirksomhedRepræsentantView.as_view(), name='virksomhed-represent'),
]
