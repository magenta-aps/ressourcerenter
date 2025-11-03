from administration.apps import AdministrationConfig
from administration.views import (
    AfgiftsperiodeCreateView,
    AfgiftsperiodeHistoryView,
    AfgiftsperiodeListView,
    AfgiftsperiodeSatsTabelUpdateView,
    AfgiftsperiodeUpdateView,
    BilagDownloadView,
    FakturaCreateView,
    FakturaDeleteView,
    FakturaDetailView,
    FakturaSendView,
    FiskeArtCreateView,
    FiskeArtHistoryView,
    FiskeArtListView,
    FiskeArtUpdateView,
    FrontpageView,
    G69CodeExportCreateView,
    G69DownloadView,
    G69ListView,
    IndberetningAfstemFormView,
    IndberetningDetailView,
    IndberetningListLinjeView,
    IndberetningListView,
    IndberetningsLinjeListView,
    PostLoginView,
    ProduktTypeCreateView,
    ProduktTypeHistoryView,
    ProduktTypeListView,
    ProduktTypeUpdateView,
    SatsTabelElementHistoryView,
    VirksomhedCreateView,
    VirksomhedListView,
    VirksomhedRepræsentantStopView,
    VirksomhedRepræsentantView,
    VirksomhedUpdateView,
)
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

app_name = AdministrationConfig.name

urlpatterns = [
    path("postlogin/", PostLoginView.as_view(), name="postlogin"),
    path("", FrontpageView.as_view(), name="frontpage"),
    path(
        "login/",
        LoginView.as_view(template_name="administration/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "afgiftsperiode/", AfgiftsperiodeListView.as_view(), name="afgiftsperiode-list"
    ),
    path(
        "afgiftsperiode/create",
        AfgiftsperiodeCreateView.as_view(),
        name="afgiftsperiode-create",
    ),
    path(
        "afgiftsperiode/<uuid:pk>/update",
        AfgiftsperiodeUpdateView.as_view(),
        name="afgiftsperiode-update",
    ),
    path(
        "afgiftsperiode/<uuid:pk>/satstabel",
        AfgiftsperiodeSatsTabelUpdateView.as_view(),
        name="afgiftsperiode-satstabel",
    ),
    path(
        "afgiftsperiode/<uuid:pk>/history/",
        AfgiftsperiodeHistoryView.as_view(),
        name="afgiftsperiode-history",
    ),
    path(
        "satstabelelement/<int:pk>/history/",
        SatsTabelElementHistoryView.as_view(),
        name="satstabelelement-history",
    ),
    path("fiskeart/", FiskeArtListView.as_view(), name="fiskeart-list"),
    path("fiskeart/create", FiskeArtCreateView.as_view(), name="fiskeart-create"),
    path(
        "fiskeart/<uuid:pk>/update",
        FiskeArtUpdateView.as_view(),
        name="fiskeart-update",
    ),
    path(
        "fiskeart/<uuid:pk>/history/",
        FiskeArtHistoryView.as_view(),
        name="fiskeart-history",
    ),
    path("produkttype/", ProduktTypeListView.as_view(), name="produkttype-list"),
    path(
        "produkttype/create", ProduktTypeCreateView.as_view(), name="produkttype-create"
    ),
    path(
        "produkttype/<uuid:pk>/update",
        ProduktTypeUpdateView.as_view(),
        name="produkttype-update",
    ),
    path(
        "produkttype/<uuid:pk>/history/",
        ProduktTypeHistoryView.as_view(),
        name="produkttype-history",
    ),
    path("indberetning/", IndberetningListView.as_view(), name="indberetning-list"),
    path(
        "indberetning/<uuid:pk>/linjer",
        IndberetningListLinjeView.as_view(),
        name="indberetning-linjer",
    ),
    path(
        "indberetning/<uuid:pk>/",
        IndberetningDetailView.as_view(),
        name="indberetning-detail",
    ),
    path(
        "indberetning/<uuid:pk>/afstem",
        IndberetningAfstemFormView.as_view(),
        name="indberetning-afstem",
    ),
    path(
        "indberetningslinje/afstem",
        IndberetningsLinjeListView.as_view(),
        name="indberetningslinje-list",
    ),
    path(
        "faktura/create/<uuid:pk>", FakturaCreateView.as_view(), name="faktura-create"
    ),
    path("faktura/<int:pk>", FakturaDetailView.as_view(), name="faktura-detail"),
    path("faktura/<int:pk>/send", FakturaSendView.as_view(), name="faktura-send"),
    path("faktura/<int:pk>/delete", FakturaDeleteView.as_view(), name="faktura-delete"),
    path("virksomhed/", VirksomhedListView.as_view(), name="virksomhed-list"),
    path("virksomhed/create", VirksomhedCreateView.as_view(), name="virksomhed-create"),
    path(
        "virksomhed/<uuid:pk>/",
        VirksomhedUpdateView.as_view(),
        name="virksomhed-update",
    ),
    path(
        "virksomhed/repræsenter/stop/",
        VirksomhedRepræsentantStopView.as_view(),
        name="virksomhed-represent-stop",
    ),
    path(
        "virksomhed/<uuid:pk>/repræsenter/",
        VirksomhedRepræsentantView.as_view(),
        name="virksomhed-represent",
    ),
    path("g69kode/", G69ListView.as_view(), name="g69-list"),
    path("g69kode/create/", G69CodeExportCreateView.as_view(), name="g69-create"),
    path("g69kode/<uuid:pk>/", G69DownloadView.as_view(), name="g69-download"),
    path("bilag/<uuid:pk>/", BilagDownloadView.as_view(), name="bilag-download"),
]
