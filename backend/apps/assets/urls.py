from django.urls import path
from .views import AssetViewSet, NetworkInterfaceViewSet

asset_list = AssetViewSet.as_view({"get": "list", "post": "create"})
asset_detail = AssetViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
asset_archive = AssetViewSet.as_view({"post": "archive"})
asset_restore = AssetViewSet.as_view({"post": "restore"})

iface_list = NetworkInterfaceViewSet.as_view({"get": "list", "post": "create"})
iface_detail = NetworkInterfaceViewSet.as_view({"get": "retrieve", "patch": "partial_update"})

urlpatterns = [
    path("", asset_list, name="asset_list"),
    path("<int:pk>/", asset_detail, name="asset_detail"),
    path("<int:pk>/archive/", asset_archive, name="asset_archive"),
    path("<int:pk>/restore/", asset_restore, name="asset_restore"),
]
