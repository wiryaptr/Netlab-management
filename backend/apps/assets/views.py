from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Asset, NetworkInterface
from .serializers import AssetSerializer, NetworkInterfaceSerializer


class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Asset.objects.all()
        include_archived = self.request.query_params.get("include_archived", "false").lower() == "true"
        if not include_archived:
            qs = qs.filter(archived_at__isnull=True)
        
        asset_type = self.request.query_params.get("asset_type")
        if asset_type:
            qs = qs.filter(asset_type=asset_type)
            
        status_val = self.request.query_params.get("status")
        if status_val:
            qs = qs.filter(status=status_val)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(serial_number__icontains=search)

        return qs.order_by("name", "created_at", "id")

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        asset = self.get_object()
        if asset.archived_at is not None:
            return Response({"error": {"code": "validation_error", "message": "Aset sudah terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        
        # Archive child interfaces in same transaction
        now = timezone.now()
        asset.interfaces.filter(archived_at__isnull=True).update(archived_at=now, updated_at=now)
        asset.archived_at = now
        asset.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        asset = self.get_object()
        if asset.archived_at is None:
            return Response({"error": {"code": "validation_error", "message": "Aset tidak dalam status terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        asset.archived_at = None
        asset.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(asset).data)


class NetworkInterfaceViewSet(viewsets.ModelViewSet):
    serializer_class = NetworkInterfaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = NetworkInterface.objects.all()
        include_archived = self.request.query_params.get("include_archived", "false").lower() == "true"
        if not include_archived:
            qs = qs.filter(archived_at__isnull=True)
            
        asset_id = self.request.query_params.get("asset")
        if asset_id:
            qs = qs.filter(asset_id=asset_id)

        return qs.order_by("asset_id", "name", "id")
