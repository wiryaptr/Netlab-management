from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VLAN
from .serializers import VLANSerializer


class VLANViewSet(viewsets.ModelViewSet):
    serializer_class = VLANSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = VLAN.objects.all()
        include_archived = self.request.query_params.get("include_archived", "false").lower() == "true"
        if not include_archived:
            qs = qs.filter(archived_at__isnull=True)
            
        status_val = self.request.query_params.get("status")
        if status_val:
            qs = qs.filter(status=status_val)

        return qs.order_by("vlan_number", "id")

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        vlan = self.get_object()
        if vlan.archived_at is not None:
            return Response({"error": {"code": "validation_error", "message": "VLAN sudah terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check subnet dependents
        if vlan.subnet_set.filter(archived_at__isnull=True).exists():
            return Response({"error": {"code": "has_dependents", "message": "VLAN masih dirujuk subnet aktif.", "details": {}}}, status=status.HTTP_409_CONFLICT)

        vlan.archived_at = timezone.now()
        vlan.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(vlan).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        vlan = self.get_object()
        if vlan.archived_at is None:
            return Response({"error": {"code": "validation_error", "message": "VLAN tidak dalam status terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        vlan.archived_at = None
        vlan.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(vlan).data)
