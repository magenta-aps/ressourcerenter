from django.urls import path
from indberetning.views import CreateInberetningCreateView, CompanySelect, IndberetningsListView
from indberetning.apps import IndberetningConfig

app_name = IndberetningConfig.name

urlpatterns = [
    path('create/', CreateInberetningCreateView.as_view(), name='indberetning-create'),
    path('company-select/', CompanySelect.as_view(), name='company-select'),
    path('list/', IndberetningsListView.as_view(), name='indberetning-list')
]
