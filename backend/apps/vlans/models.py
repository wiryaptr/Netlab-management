from django.db import models

class VLAN(models.Model):
    STATUSES = [("planned", "Planned"), ("active", "Active"), ("deprecated", "Deprecated")]
    vlan_number = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(default="", blank=True)
    status = models.CharField(max_length=16, choices=STATUSES)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vlans_vlan"
        constraints = [
            models.UniqueConstraint(fields=["vlan_number"], condition=models.Q(archived_at__isnull=True), name="vlans_vlan_number_active_uq"),
        ]

    def __str__(self):
        return f"{self.vlan_number}:{self.name}"
