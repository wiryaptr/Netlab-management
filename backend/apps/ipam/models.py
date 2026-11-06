from django.db import models


class Subnet(models.Model):
    """Subnet model according to DATA_MODEL.md §5.5."""

    STATUSES = [
        ("planned", "Planned"),
        ("active", "Active"),
        ("deprecated", "Deprecated"),
    ]

    cidr = models.CharField(max_length=50)
    gateway = models.CharField(max_length=50, null=True, blank=True)
    vlan = models.ForeignKey(
        "vlans.VLAN", on_delete=models.PROTECT, null=True, blank=True, db_column="vlan_id"
    )
    description = models.TextField(default="", blank=True)
    status = models.CharField(max_length=16, choices=STATUSES)

    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ipam_subnet"


class IPAddress(models.Model):
    """IPAddress model according to DATA_MODEL.md §5.6."""

    STATUSES = [
        ("allocated", "Allocated"),
        ("reserved", "Reserved"),
        ("released", "Released"),
    ]

    address = models.CharField(max_length=50)
    subnet = models.ForeignKey(
        Subnet, on_delete=models.PROTECT, related_name="ip_addresses"
    )
    status = models.CharField(max_length=16, choices=STATUSES)
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, null=True, blank=True
    )
    interface = models.ForeignKey(
        "assets.NetworkInterface", on_delete=models.PROTECT, null=True, blank=True
    )
    description = models.TextField(default="", blank=True)

    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ipam_ipaddress"
        constraints = [
            models.UniqueConstraint(
                fields=["subnet", "address"],
                condition=models.Q(archived_at__isnull=True),
                name="ipam_ipaddress_active_uq",
            ),
        ]
