from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Subnet, IPAddress
from .serializers import SubnetSerializer, IPAddressSerializer


class SubnetViewSet(viewsets.ModelViewSet):
    serializer_class = SubnetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Subnet.objects.all()
        include_archived = self.request.query_params.get("include_archived", "false").lower() == "true"
        if not include_archived:
            qs = qs.filter(archived_at__isnull=True)
            
        status_val = self.request.query_params.get("status")
        if status_val:
            qs = qs.filter(status=status_val)

        vlan_id = self.request.query_params.get("vlan")
        if vlan_id:
            qs = qs.filter(vlan_id=vlan_id)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(cidr__icontains=search) | qs.filter(description__icontains=search)

        return qs.order_by("cidr", "id")

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        subnet = self.get_object()
        if subnet.archived_at is not None:
            return Response({"error": {"code": "validation_error", "message": "Subnet sudah terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        
        if subnet.ip_addresses.filter(archived_at__isnull=True).exists():
            return Response({"error": {"code": "has_dependents", "message": "Subnet memiliki alamat IP aktif.", "details": {}}}, status=status.HTTP_409_CONFLICT)

        subnet.archived_at = timezone.now()
        subnet.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(subnet).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        subnet = self.get_object()
        if subnet.archived_at is None:
            return Response({"error": {"code": "validation_error", "message": "Subnet tidak dalam status terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        subnet.archived_at = None
        subnet.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(subnet).data)


class IPAddressViewSet(viewsets.ModelViewSet):
    serializer_class = IPAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = IPAddress.objects.all()
        include_archived = self.request.query_params.get("include_archived", "false").lower() == "true"
        if not include_archived:
            qs = qs.filter(archived_at__isnull=True)

        subnet_id = self.request.query_params.get("subnet")
        if subnet_id:
            qs = qs.filter(subnet_id=subnet_id)

        status_val = self.request.query_params.get("status")
        if status_val:
            qs = qs.filter(status=status_val)

        return qs.order_by("address", "id")

    @action(detail=True, methods=["post"])
    def release(self, request, pk=None):
        ip = self.get_object()
        if ip.status == "released" or ip.archived_at is not None:
            return Response({"error": {"code": "validation_error", "message": "IP sudah dilepas.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        
        ip.status = "released"
        ip.archived_at = timezone.now()
        ip.save(update_fields=["status", "archived_at", "updated_at"])
        return Response(self.get_serializer(ip).data)
