from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Incident, IncidentEvent
from .serializers import IncidentSerializer, IncidentEventSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Incident.objects.all()
        status_val = self.request.query_params.get("status")
        if status_val:
            qs = qs.filter(status=status_val)
        severity = self.request.query_params.get("severity")
        if severity:
            qs = qs.filter(severity=severity)
        return qs.order_by("-created_at", "id")

    @action(detail=True, methods=["post"])
    def events(self, request, pk=None):
        incident = self.get_object()
        if incident.status == "closed":
            return Response({"error": {"code": "incident_closed", "message": "Insiden tertutup tidak dapat ditambah.", "details": {}}}, status=status.HTTP_409_CONFLICT)
        serializer = IncidentEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        actor = request.user
        event = IncidentEvent.objects.create(
            incident=incident,
            actor=actor,
            event_type=serializer.validated_data.get("event_type", "note"),
            body=serializer.validated_data.get("body", ""),
            from_value=serializer.validated_data.get("from_value"),
            to_value=serializer.validated_data.get("to_value"),
        )
        return Response(serializer(instance=event).data)


class IncidentEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IncidentEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        incident_id = self.kwargs.get("incident_id")
        if incident_id is None:
            return IncidentEvent.objects.none()
        return IncidentEvent.objects.filter(incident_id=incident_id).order_by("created_at", "id")
