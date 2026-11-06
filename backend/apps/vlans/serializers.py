from rest_framework import serializers
from .models import VLAN


class VLANSerializer(serializers.ModelSerializer):
    class Meta:
        model = VLAN
        fields = [
            "id",
            "vlan_number",
            "name",
            "description",
            "status",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "archived_at", "created_at", "updated_at"]

    def validate_vlan_number(self, value):
        if not (1 <= value <= 4094):
            raise serializers.ValidationError("Nomor VLAN harus berada di antara 1 dan 4094.")
        if 1002 <= value <= 1005:
            raise serializers.ValidationError("Nomor VLAN 1002 sampai 1005 dicadangkan dan tidak diizinkan.")
        return value
