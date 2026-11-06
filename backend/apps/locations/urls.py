from django.urls import path
from .views import LocationViewSet

location_list = LocationViewSet.as_view({"get": "list", "post": "create"})
location_detail = LocationViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
location_archive = LocationViewSet.as_view({"post": "archive"})
location_restore = LocationViewSet.as_view({"post": "restore"})

urlpatterns = [
    path("", location_list, name="location_list"),
    path("<int:pk>/", location_detail, name="location_detail"),
    path("<int:pk>/archive/", location_archive, name="location_archive"),
    path("<int:pk>/restore/", location_restore, name="location_restore"),
]
