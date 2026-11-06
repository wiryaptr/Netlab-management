from django.db import models


class Connection(models.Model):
    """Connection model according to DATA_MODEL.md §5.8."""

    STATUSES = [("ethernet", "ethernet"), ("fiber", "fiber"), ("console", "console"), ("wireless", "wireless"), ("virtual", "virtual")]

    interface_a = models.ForeignKey(
        "assets.NetworkInterface",
        on_delete=models.PROTECT,
        related_name="connection_a",
        db_column="interface_a_id",
    )
    interface_b = models.ForeignKey(
        "assets.NetworkInterface",
        on_delete=models.PROTECT,
        related_name="connection_b",
        db_column="interface_b_id",
    )
    connection_type = models.CharField(max_length=16, choices=STATUSES)
    description = models.TextField(default="", blank=True)

    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "connections_connection"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(interface_a_id__lt=models.F("interface_b_id")),
                name="connections_connection_order_chk",
            ),
            models.UniqueConstraint(
                fields=["interface_a", "interface_b"],
                condition=models.Q(archived_at__isnull=True),
                name="connections_connection_pair_active_uq",
            ),
        ]

    def __str__(self):
        return f"{self.interface_a} <-> {self.interface_b}"
