from accounts.models import User


def record_audit(actor, action, object_type, object_id=None, safe_metadata=None, actor_username=None):
    from .models import AuditEvent
    return AuditEvent.objects.create(
        actor=actor,
        actor_username=actor_username or (actor.username if actor else None),
        action=action,
        object_type=object_type,
        object_id=object_id,
        safe_metadata=safe_metadata or {},
    )
