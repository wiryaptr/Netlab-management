from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/auth/", include("apps.accounts.urls_auth")),
    path("api/v1/users/", include("apps.accounts.urls_users")),
    path("api/v1/locations/", include("apps.locations.urls")),
    path("api/v1/assets/", include("apps.assets.urls")),
    path("api/v1/interfaces/", include("apps.assets.urls_interfaces")),
    path("api/v1/subnets/", include("apps.ipam.urls_subnets")),
    path("api/v1/ip-addresses/", include("apps.ipam.urls_ipaddresses")),
    path("api/v1/vlans/", include("apps.vlans.urls")),
    path("api/v1/connections/", include("apps.connections.urls")),
    path("api/v1/incidents/", include("apps.incidents.urls")),
    path("api/v1/imports/", include("apps.imports.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
]