from django.urls import path
from .views import IPAddressViewSet

ip_list = IPAddressViewSet.as_view({"get": "list", "post": "create"})
ip_detail = IPAddressViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
ip_release = IPAddressViewSet.as_view({"post": "release"})

urlpatterns = [
    path("", ip_list, name="ipaddress_list"),
    path("<int:pk>/", ip_detail, name="ipaddress_detail"),
    path("<int:pk>/release/", ip_release, name="ipaddress_release"),
]
