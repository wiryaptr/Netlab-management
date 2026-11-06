from django.urls import path
from .views import IncidentViewSet, IncidentEventViewSet

incident_list = IncidentViewSet.as_view({"get": "list", "post": "create"})
incident_detail = IncidentViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
incident_events = IncidentViewSet.as_view({"get": "events", "post": "events"})

urlpatterns = [
    path("", incident_list, name="incident_list"),
    path("<int:pk>/", incident_detail, name="incident_detail"),
    path("<int:pk>/events/", incident_events, name="incident_events"),
]
