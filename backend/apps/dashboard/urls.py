from django.urls import path
from .views import DashboardSummaryView, HealthView

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="dashboard_summary"),
]
