
import json

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver

from .models import AuditLog
from .middleware import get_current_user


SENSITIVE_FIELDS = {
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "private_key",
    "session_key",
    "session_data",
    "authorization",
    "credential",
    "otp",
}


def is_sensitive(field_name):
    name = field_name.lower().replace("-", "_")
    return any(item in name for item in SENSITIVE_FIELDS)


def serialize_value(value):
    return json.loads(
        json.dumps(value, cls=DjangoJSONEncoder, default=str)
    )


def get_model_values(instance):
    values = {}

    for field in instance._meta.concrete_fields:
        if is_sensitive(field.name):
            continue

        value = getattr(instance, field.attname, None)
        values[field.name] = serialize_value(value)

    return values


def get_actor():
    user = get_current_user()

    if user and user.is_authenticated:
        return user

    return None


def write_audit_log(instance, action, changes=None, using="default"):
    if instance._meta.proxy:
        return

    if instance._meta.label_lower == AuditLog._meta.label_lower:
        return

    try:
        object_repr = str(instance)
    except Exception:
        object_repr = instance._meta.object_name

    AuditLog.objects.using(using).create(
        user=get_actor(),
        action=action,
        app_label=instance._meta.app_label,
        model_name=instance._meta.object_name,
        object_id=str(instance.pk or ""),
        object_repr=object_repr[:255],
        description=f"{instance._meta.verbose_name}: {action}",
        changes=changes or {},
    )


# -------------------------
# Login / Logout
# -------------------------

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action="login",
        app_label=user._meta.app_label,
        model_name=user._meta.object_name,
        object_id=str(user.pk),
        object_repr=str(user),
        description="ورود کاربر به سامانه",
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user is None:
        return

    AuditLog.objects.create(
        user=user,
        action="logout",
        app_label=user._meta.app_label,
        model_name=user._meta.object_name,
        object_id=str(user.pk),
        object_repr=str(user),
        description="خروج کاربر از سامانه",
    )


# -------------------------
# Save: Create / Update
# -------------------------

@receiver(pre_save)
def audit_pre_save(sender, instance, raw=False, using="default", **kwargs):

    if raw or sender._meta.proxy:
        return

    if sender._meta.label_lower == AuditLog._meta.label_lower:
        return

    instance._auditlog_old_values = None

    if instance.pk:
        try:
            old_instance = sender._base_manager.using(using).get(
                pk=instance.pk
            )
            instance._auditlog_old_values = get_model_values(old_instance)

        except sender.DoesNotExist:
            pass


@receiver(post_save)
def audit_post_save(
    sender,
    instance,
    created,
    raw=False,
    using="default",
    **kwargs
):

    if raw or sender._meta.proxy:
        return

    if sender._meta.label_lower == AuditLog._meta.label_lower:
        return

    new_values = get_model_values(instance)

    if created:
        changes = {
            key: {"old": None, "new": value}
            for key, value in new_values.items()
        }

        action = "create"

    else:
        old_values = getattr(
            instance,
            "_auditlog_old_values",
            None
        ) or {}

        changes = {}

        for key, new_value in new_values.items():
            old_value = old_values.get(key)

            if old_value != new_value:
                changes[key] = {
                    "old": old_value,
                    "new": new_value,
                }

        if not changes:
            return

        action = "update"

    write_audit_log(
        instance=instance,
        action=action,
        changes=changes,
        using=using,
    )


# -------------------------
# Delete
# -------------------------

@receiver(pre_delete)
def audit_pre_delete(sender, instance, using="default", **kwargs):

    if sender._meta.proxy:
        return

    if sender._meta.label_lower == AuditLog._meta.label_lower:
        return

    write_audit_log(
        instance=instance,
        action="delete",
        changes={
            "deleted_data": get_model_values(instance)
        },
        using=using,
    )
