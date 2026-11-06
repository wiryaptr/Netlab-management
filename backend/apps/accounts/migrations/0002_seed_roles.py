from django.db import migrations


def create_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    roles = ["administrator", "lab_manager", "lab_assistant", "viewer"]
    for role in roles:
        Group.objects.get_or_create(name=role)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "__latest__"),
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, migrations.RunPython.noop),
    ]
