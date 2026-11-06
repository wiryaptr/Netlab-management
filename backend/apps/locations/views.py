from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Location
from .serializers import LocationSerializer


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Location.objects.all()
        include_archived = self.request.query_params.get("include_archived", "false").lower() == "true"
        if not include_archived:
            qs = qs.filter(archived_at__isnull=True)
        
        loc_type = self.request.query_params.get("location_type")
        if loc_type:
            qs = qs.filter(location_type=loc_type)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        return qs.order_by("name", "created_at", "id")

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        location = self.get_object()
        if location.archived_at is not None:
            return Response({"error": {"code": "validation_error", "message": "Lokasi sudah terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check active asset dependents
        if location.asset_set.filter(archived_at__isnull=True).exists():
            return Response({"error": {"code": "has_dependents", "message": "Lokasi memiliki aset aktif.", "details": {}}}, status=status.HTTP_409_CONFLICT)

        location.archived_at = timezone.now()
        location.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(location).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        location = self.get_object()
        if location.archived_at is None:
            return Response({"error": {"code": "validation_error", "message": "Lokasi tidak dalam status terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        location.archived_at = None
        location.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(location).data)
