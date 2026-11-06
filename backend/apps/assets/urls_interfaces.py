from django.urls import path
from .views import NetworkInterfaceViewSet

iface_list = NetworkInterfaceViewSet.as_view({"get": "list", "post": "create"})
iface_detail = NetworkInterfaceViewSet.as_view({"get": "retrieve", "patch": "partial_update"})

urlpatterns = [
    path("", iface_list, name="interface_list"),
    path("<int:pk>/", iface_detail, name="interface_detail"),
]
