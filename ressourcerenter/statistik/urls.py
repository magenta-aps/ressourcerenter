from django.urls import path

from statistik.apps import StatistikConfig
from statistik.views import StatistikView, StatistikChoicesView

app_name = StatistikConfig.name

urlpatterns = [
    path("", StatistikView.as_view(), name="frontpage"),
    path("choices", StatistikChoicesView.as_view(), name="choices"),
]
