from django.db import models


class Location(models.Model):
    """Location model according to DATA_MODEL.md §5.2."""

    BUILDING = "building"
    ROOM = "room"
    RACK = "rack"
    CABINET = "cabinet"
    STORAGE = "storage"
    OTHER = "other"

    LOCATION_TYPE_CHOICES = [
        (BUILDING, "Building"),
        (ROOM, "Room"),
        (RACK, "Rack"),
        (CABINET, "Cabinet"),
        (STORAGE, "Storage"),
        (OTHER, "Other"),
    ]

    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=16, choices=LOCATION_TYPE_CHOICES)
    description = models.TextField(default="", blank=True)

    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "locations_location"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(location_type__in=["building", "room", "rack", "cabinet", "storage", "other"]),
                name="locations_location_type_chk"
            ),
        ]

    def __str__(self):
        return self.name
