import ipaddress

from rest_framework import serializers

from .models import IPAddress, Subnet


class SubnetSerializer(serializers.ModelSerializer):
    vlan_number = serializers.ReadOnlyField(source="vlan.vlan_number")
    vlan_name = serializers.ReadOnlyField(source="vlan.name")

    class Meta:
        model = Subnet
        fields = [
            "id",
            "cidr",
            "gateway",
            "vlan",
            "vlan_number",
            "vlan_name",
            "description",
            "status",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "vlan_number", "vlan_name", "archived_at", "created_at", "updated_at"]

    def validate_cidr(self, value):
        try:
            net = ipaddress.ip_network(value, strict=False)
        except ValueError:
            raise serializers.ValidationError("Format CIDR tidak valid.")

        if net.is_loopback or net.is_multicast or net.is_unspecified or net.is_link_local:
            raise serializers.ValidationError("Subnet alamat khusus (loopback/multicast/dll) tidak diizinkan.")

        # Overlap check
        qs = Subnet.objects.filter(archived_at__isnull=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        for other in qs:
            try:
                other_net = ipaddress.ip_network(other.cidr, strict=False)
                if net.overlaps(other_net):
                    raise serializers.ValidationError(f"Subnet tumpang tindih dengan {other.cidr}.")
            except ValueError:
                continue

        # Immutable check for CIDR if IP addresses exist
        if self.instance and self.instance.cidr != str(net):
            if self.instance.ip_addresses.filter(archived_at__isnull=True).exists():
                raise serializers.ValidationError("CIDR tidak dapat diubah selama ada alamat IP aktif.")

        return str(net)

    def validate_gateway(self, value):
        if not value:
            return value
        cidr = self.initial_data.get("cidr") or getattr(self.instance, "cidr", None)
        if cidr:
            try:
                net = ipaddress.ip_network(cidr, strict=False)
                if ipaddress.ip_address(value) not in net:
                    raise serializers.ValidationError("Gateway harus berada dalam subnet.")
            except ValueError:
                pass
        return value

    def validate_vlan(self, value):
        if value and value.archived_at is not None:
            raise serializers.ValidationError("VLAN sudah terarsip.")
        return value


class IPAddressSerializer(serializers.ModelSerializer):
    subnet_cidr = serializers.ReadOnlyField(source="subnet.cidr")
    asset_name = serializers.ReadOnlyField(source="asset.name")
    interface_name = serializers.ReadOnlyField(source="interface.name")

    class Meta:
        model = IPAddress
        fields = [
            "id",
            "address",
            "subnet",
            "subnet_cidr",
            "status",
            "asset",
            "asset_name",
            "interface",
            "interface_name",
            "description",
            "archived_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "subnet_cidr",
            "asset_name",
            "interface_name",
            "archived_at",
            "created_at",
            "updated_at",
        ]

    def validate_address(self, value):
        try:
            addr = ipaddress.ip_address(value)
        except ValueError:
            raise serializers.ValidationError("Format alamat IP tidak valid.")
        return str(addr)

    def validate(self, data):
        addr_str = data.get("address") or getattr(self.instance, "address", None)
        subnet_obj = data.get("subnet") or getattr(self.instance, "subnet", None)

        if not addr_str or not subnet_obj:
            return data

        addr = ipaddress.ip_address(addr_str)
        net = ipaddress.ip_network(subnet_obj.cidr, strict=False)

        if addr not in net:
            raise serializers.ValidationError({"address": "Alamat IP harus berada dalam subnet."})

        # Reject network/broadcast for IPv4 < /31
        if net.version == 4 and net.prefixlen < 31:
            if addr == net.network_address:
                raise serializers.ValidationError({"address": "Network address tidak diizinkan."})
            if addr == net.broadcast_address:
                raise serializers.ValidationError({"address": "Broadcast address tidak diizinkan."})

        # Immutable check
        if self.instance:
            if data.get("address") and data["address"] != self.instance.address:
                raise serializers.ValidationError({"address": "Alamat IP bersifat immutable."})
            if data.get("subnet") and data["subnet"] != self.instance.subnet:
                raise serializers.ValidationError({"subnet": "Relasi subnet bersifat immutable."})

        # Uniqueness active check
        qs = IPAddress.objects.filter(subnet=subnet_obj, address=str(addr), archived_at__isnull=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({"address": "Alamat IP sudah dialokasikan pada subnet ini."})

        # Interface/Asset validation
        asset = data.get("asset") or getattr(self.instance, "asset", None)
        interface = data.get("interface") or getattr(self.instance, "interface", None)
        if interface and not asset:
            raise serializers.ValidationError({"asset": "Aset wajib diisi jika interface ditentukan."})
        if interface and asset and interface.asset_id != asset.id:
            raise serializers.ValidationError({"interface": "Interface harus milik aset yang dipilih."})

        return data
