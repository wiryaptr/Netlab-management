from django.db import models


class AuditEvent(models.Model):
    actor = models.ForeignKey("accounts.User", on_delete=models.PROTECT, null=True, blank=True)
    actor_username = models.CharField(max_length=150, null=True, blank=True)
    action = models.CharField(max_length=48)
    object_type = models.CharField(max_length=24)
    object_id = models.BigIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    safe_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_auditevent"
        ordering = ["-timestamp"]
