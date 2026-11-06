from rest_framework import serializers
from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "location_type",
            "description",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "archived_at", "created_at", "updated_at"]

    def validate_name(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Nama lokasi tidak boleh kosong.")
        return val
