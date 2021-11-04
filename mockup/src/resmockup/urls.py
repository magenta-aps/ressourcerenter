# Urls for the resmockup app

from django.urls import path
from resmockup import views

urlpatterns = [
    path(r'run/create', views.RunCalculationView.as_view(), name='run-create'),
    path(r'run/', views.ListSimulationView.as_view(), name='run-list'),
    path(r'calc/', views.ListCalculationView.as_view(), name='calc-list'),
    path(r'calc/create', views.CreateCalculationView.as_view(), name='calc-create'),
    path(r'calc/edit', views.EditCalculationView.as_view(), name='calc-edit'),
    path(r'form/edit', views.EditFormView.as_view(), name='form-edit'),
    path(r'field/edit', views.EditFormFieldView.as_view(), name='field-edit'),
    path(r'fish/edit', views.EditFishView.as_view(), name='fish-edit'),
    path(r'period/edit', views.EditPeriodView.as_view(), name='period-edit'),
    path(r'period/', views.ListPeriodView.as_view(), name='period-list'),
    path(r'period/sats', views.EditSatsView.as_view(), name='period-sats'),
    path(r'report', views.CreateReportView.as_view(), name='report'),
    path(r'report1', views.CreateReportView1.as_view(), name='report1'),
    path(r'report2', views.CreateReportView2.as_view(), name='report2'),
    path(r'report3', views.CreateReportView3.as_view(), name='report3'),
    path(r'report4', views.CreateReportView4.as_view(), name='report4')
]
