import re

from rest_framework import serializers

from .models import Asset, NetworkInterface

MAC_RE = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$")


class NetworkInterfaceSerializer(serializers.ModelSerializer):
    asset_name = serializers.ReadOnlyField(source="asset.name")

    class Meta:
        model = NetworkInterface
        fields = [
            "id",
            "asset",
            "asset_name",
            "name",
            "mac_address",
            "description",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "asset_name", "archived_at", "created_at", "updated_at"]

    def validate_mac_address(self, value):
        if value in (None, ""):
            return None
        normalized = value.strip().lower().replace("-", ":")
        if not MAC_RE.match(normalized):
            raise serializers.ValidationError("MAC address harus EUI-48 (contoh 00:1a:2b:3c:4d:5e).")
        return normalized

    def validate(self, data):
        asset = data.get("asset") or getattr(self.instance, "asset", None)
        name = data.get("name") or getattr(self.instance, "name", None)
        if asset and asset.archived_at is not None:
            raise serializers.ValidationError({"asset": "Aset sudah terarsip."})
        if asset and name:
            qs = NetworkInterface.objects.filter(
                asset=asset, name__iexact=name, archived_at__isnull=True
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"name": "Nama interface sudah digunakan pada aset ini."})
        return data


class AssetSerializer(serializers.ModelSerializer):
    location_name = serializers.ReadOnlyField(source="location.name")

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "asset_type",
            "manufacturer",
            "model",
            "serial_number",
            "status",
            "location",
            "location_name",
            "description",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "location_name", "archived_at", "created_at", "updated_at"]

    def validate_name(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Nama aset tidak boleh kosong.")
        qs = Asset.objects.filter(name__iexact=val, archived_at__isnull=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Nama aset sudah digunakan.")
        return val

    def validate_serial_number(self, value):
        if value in (None, ""):
            return None
        qs = Asset.objects.filter(serial_number=value, archived_at__isnull=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Serial number sudah digunakan.")
        return value

    def validate_location(self, value):
        if value and value.archived_at is not None:
            raise serializers.ValidationError("Lokasi sudah terarsip.")
        return value
