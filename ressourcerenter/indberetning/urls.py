from django.urls import path
from django.views.generic import TemplateView
from indberetning.apps import IndberetningConfig
from indberetning.views import (
    CreateIndberetningCreateView,
    IndberetningsListView,
    SelectIndberetningsType,
    Frontpage,
    VirksomhedUpdateView,
    UpdateIndberetningsView,
    BilagDownloadView,
    IndberetningCalculateJsonView,
    IndberetningListLinjeView,
)

app_name = IndberetningConfig.name

urlpatterns = [
    path("", Frontpage.as_view(), name="frontpage"),
    path(
        "company/<uuid:pk>/edit/", VirksomhedUpdateView.as_view(), name="company-edit"
    ),
    path("list/", IndberetningsListView.as_view(), name="indberetning-list"),
    path(
        "<uuid:pk>/linjer",
        IndberetningListLinjeView.as_view(),
        name="indberetning-linjer",
    ),
    path("select/", SelectIndberetningsType.as_view(), name="type-select"),
    path(
        "calculate",
        IndberetningCalculateJsonView.as_view(),
        name="indberetning-calculate",
    ),
    path(
        "<uuid:periode>/<int:skema>/create/",
        CreateIndberetningCreateView.as_view(),
        name="indberetning-create",
    ),
    path(
        "<uuid:pk>/edit/",
        UpdateIndberetningsView.as_view(),
        name="indberetning-edit",
    ),
    path("bilag/<uuid:pk>/", BilagDownloadView.as_view(), name="bilag-download"),
    path(
        "no_cvr",
        TemplateView.as_view(template_name="indberetning/no_cvr.html"),
        name="no-cvr",
    ),
]
