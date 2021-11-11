from django.urls import path
from indberetning.views import CreateInberetningCreateView, CompanySelect, IndberetningsListView, \
    SelectIndberetningsType, CreateIndhandlingsCreateView
from indberetning.apps import IndberetningConfig

app_name = IndberetningConfig.name

urlpatterns = [
    path('company-select/', CompanySelect.as_view(), name='company-select'),
    path('list/', IndberetningsListView.as_view(), name='indberetning-list'),
    path('select/', SelectIndberetningsType.as_view(), name='type-select'),
    path('create/', CreateInberetningCreateView.as_view(), name='indberetning-create'),
    path('indhandling/', CreateIndhandlingsCreateView.as_view(), name='indhandling-create')
]
