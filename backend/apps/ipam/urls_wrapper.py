from django.urls import include, path
from .urls_subnets import urlpatterns_subnets
from .urls_ipaddresses import urlpatterns_ipaddresses

urlpatterns = [
    # Subnets & IP addresses are split or combined; wire subnets here as default
] + urlpatterns_subnets
