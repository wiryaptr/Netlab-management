from django.urls import path
from .views import SubnetViewSet, IPAddressViewSet

subnet_list = SubnetViewSet.as_view({"get": "list", "post": "create"})
subnet_detail = SubnetViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
subnet_archive = SubnetViewSet.as_view({"post": "archive"})
subnet_restore = SubnetViewSet.as_view({"post": "restore"})

ip_list = IPAddressViewSet.as_view({"get": "list", "post": "create"})
ip_detail = IPAddressViewSet.as_view({"get": "retrieve", "patch": "partial_update"})
ip_release = IPAddressViewSet.as_view({"post": "release"})

urlpatterns = [
    path("subnets/", subnet_list, name="subnet_list"),
    path("subnets/<int:pk>/", subnet_detail, name="subnet_detail"),
    path("subnets/<int:pk>/archive/", subnet_archive, name="subnet_archive"),
    path("subnets/<int:pk>/restore/", subnet_restore, name="subnet_restore"),
    path("ip-addresses/", ip_list, name="ipaddress_list"),
    path("ip-addresses/<int:pk>/", ip_detail, name="ipaddress_detail"),
    path("ip-addresses/<int:pk>/release/", ip_release, name="ipaddress_release"),
]
