from django.db import models


class Incident(models.Model):
    STATUSES = [("open", "Open"), ("in_progress", "In Progress"), ("resolved", "Resolved"), ("closed", "Closed")]
    SEVERITIES = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")]

    title = models.CharField(max_length=200)
    description = models.TextField(default="", blank=True)
    severity = models.CharField(max_length=16, choices=SEVERITIES)
    status = models.CharField(max_length=16, choices=STATUSES, default="open")
    assignee = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, null=True, blank=True
    )
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "incidents_incident"


class IncidentEvent(models.Model):
    EVENT_TYPES = [("created", "Created"), ("note", "Note"), ("status_changed", "Status Changed"), ("severity_changed", "Severity Changed"), ("assignee_changed", "Assignee Changed"), ("asset_changed", "Asset Changed")]

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="events")
    actor = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    event_type = models.CharField(max_length=24, choices=EVENT_TYPES)
    body = models.TextField(default="", blank=True)
    from_value = models.CharField(max_length=100, null=True, blank=True)
    to_value = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "incidents_incidentevent"
