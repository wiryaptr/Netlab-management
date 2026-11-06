from rest_framework import serializers
from .models import Connection


class ConnectionSerializer(serializers.ModelSerializer):
    interface_a_label = serializers.ReadOnlyField(source="interface_a.__str__")
    interface_b_label = serializers.ReadOnlyField(source="interface_b.__str__")

    class Meta:
        model = Connection
        fields = [
            "id",
            "interface_a",
            "interface_b",
            "interface_a_label",
            "interface_b_label",
            "connection_type",
            "description",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "interface_a_label",
            "interface_b_label",
            "archived_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        ia = data.get("interface_a")
        ib = data.get("interface_b")
        if ia and ib and ia.id == ib.id:
            raise serializers.ValidationError("Interface A dan B harus berbeda.")
        if ia and ib and ia.id > ib.id:
            data["interface_a"], data["interface_b"] = ib, ia
        return data
