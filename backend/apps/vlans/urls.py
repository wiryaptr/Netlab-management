from django.urls import path
from .views import VLANViewSet

vlan_list = VLANViewSet.as_view({"get": "list", "post": "create"})
vlan_detail = VLANViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
vlan_archive = VLANViewSet.as_view({"post": "archive"})
vlan_restore = VLANViewSet.as_view({"post": "restore"})

urlpatterns = [
    path("", vlan_list, name="vlan_list"),
    path("<int:pk>/", vlan_detail, name="vlan_detail"),
    path("<int:pk>/archive/", vlan_archive, name="vlan_archive"),
    path("<int:pk>/restore/", vlan_restore, name="vlan_restore"),
]
