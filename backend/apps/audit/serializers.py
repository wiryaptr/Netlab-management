from rest_framework import serializers
from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "actor",
            "actor_username",
            "action",
            "object_type",
            "object_id",
            "timestamp",
            "safe_metadata",
        ]
        read_only_fields = fields
