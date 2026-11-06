from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Connection
from .serializers import ConnectionSerializer


class ConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Connection.objects.all()
        include_archived = self.request.query_params.get("include_archived", "false").lower() == "true"
        if not include_archived:
            qs = qs.filter(archived_at__isnull=True)
            
        con_type = self.request.query_params.get("connection_type")
        if con_type:
            qs = qs.filter(connection_type=con_type)

        return qs.order_by("id")

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        conn = self.get_object()
        if conn.archived_at is not None:
            return Response({"error": {"code": "validation_error", "message": "Koneksi sudah terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        conn.archived_at = timezone.now()
        conn.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(conn).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        conn = self.get_object()
        if conn.archived_at is None:
            return Response({"error": {"code": "validation_error", "message": "Koneksi tidak dalam status terarsip.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        conn.archived_at = None
        conn.save(update_fields=["archived_at", "updated_at"])
        return Response(self.get_serializer(conn).data)
