from rest_framework import serializers
from .models import Incident, IncidentEvent


class IncidentEventSerializer(serializers.ModelSerializer):
    actor_username = serializers.ReadOnlyField(source="actor.username")

    class Meta:
        model = IncidentEvent
        fields = [
            "id",
            "incident",
            "actor",
            "actor_username",
            "event_type",
            "body",
            "from_value",
            "to_value",
            "created_at",
        ]
        read_only_fields = ["id", "actor_username", "created_at"]


class IncidentSerializer(serializers.ModelSerializer):
    asset_name = serializers.ReadOnlyField(source="asset.name")
    assignee_username = serializers.ReadOnlyField(source="assignee.username")

    class Meta:
        model = Incident
        fields = [
            "id",
            "title",
            "description",
            "severity",
            "status",
            "assignee",
            "assignee_username",
            "asset",
            "asset_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "asset_name", "assignee_username", "created_at", "updated_at"]
