from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


username_validator = RegexValidator(
    regex=r'^[a-z0-9._-]{3,150}$',
    message="Username harus huruf kecil, angka, titik, underscore, atau strip (-). Minimal 3 karakter."
)


class User(AbstractUser):
    """Custom user model for NetLab Manager."""

    username_validator = username_validator

    # Override username field with validator
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Harus huruf kecil, minimal 3 karakter.",
        validators=[username_validator],
        error_messages={
            "unique": "Username sudah digunakan.",
        },
    )

    first_name = models.CharField(max_length=150, default="")
    last_name = models.CharField(max_length=150, default="")
    email = models.EmailField(max_length=254, unique=True, default="")

    # Additional fields
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Role assignment
    must_change_password = models.BooleanField(default=False)

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Normalize username to lowercase before saving
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)

    @property
    def role(self):
        """Return the user's primary role (first group)."""
        groups = self.groups.all()
        if groups.exists():
            return groups[0].name
        return "viewer"

    @property
    def permissions(self):
        """Return effective permission codenames."""
        from django.contrib.auth.models import Permission
        user_perms = set()
        for group in self.groups.all():
            for perm in group.permissions.all():
                user_perms.add(perm.codename)
        return user_perms