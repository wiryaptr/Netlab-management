from django.db import models


class Asset(models.Model):
    """Asset model according to DATA_MODEL.md §5.3."""

    ASSET_TYPES = [
        ("router", "Router"),
        ("switch", "Switch"),
        ("access_point", "Access Point"),
        ("firewall", "Firewall"),
        ("server", "Server"),
        ("workstation", "Workstation"),
        ("patch_panel", "Patch Panel"),
        ("other", "Other"),
    ]
    STATUSES = [
        ("in_use", "In Use"),
        ("spare", "Spare"),
        ("maintenance", "Maintenance"),
        ("retired", "Retired"),
    ]

    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=16, choices=ASSET_TYPES)
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUSES)
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="location_id",
    )
    description = models.TextField(default="", blank=True)

    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_asset"
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(archived_at__isnull=True),
                name="assets_asset_name_active_uq",
            ),
            models.UniqueConstraint(
                fields=["serial_number"],
                condition=models.Q(archived_at__isnull=True, serial_number__isnull=False),
                name="assets_asset_serial_active_uq",
            ),
        ]

    def __str__(self):
        return self.name


class NetworkInterface(models.Model):
    """Network interface model according to DATA_MODEL.md §5.4."""

    asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT, related_name="interfaces", db_column="asset_id"
    )
    name = models.CharField(max_length=64)
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    description = models.TextField(default="", blank=True)

    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_networkinterface"
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "name"],
                condition=models.Q(archived_at__isnull=True),
                name="assets_networkinterface_name_active_uq",
            ),
        ]

    def __str__(self):
        return f"{self.asset.name}:{self.name}"
