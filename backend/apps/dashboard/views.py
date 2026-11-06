from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.assets.models import Asset
from apps.locations.models import Location
from apps.ipam.models import Subnet, IPAddress
from apps.vlans.models import VLAN
from apps.connections.models import Connection
from apps.incidents.models import Incident


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "locations": Location.objects.filter(archived_at__isnull=True).count(),
                "assets": Asset.objects.filter(archived_at__isnull=True).count(),
                "subnets": Subnet.objects.filter(archived_at__isnull=True).count(),
                "ip_addresses": IPAddress.objects.filter(archived_at__isnull=True).count(),
                "vlans": VLAN.objects.filter(archived_at__isnull=True).count(),
                "connections": Connection.objects.filter(archived_at__isnull=True).count(),
                "open_incidents": Incident.objects.exclude(status="closed").count(),
            },
            status=status.HTTP_200_OK,
        )
