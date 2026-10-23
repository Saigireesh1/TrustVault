from django.conf import settings
from django.db import models
from django.utils import timezone

class AuditChainState(models.Model):
    """Singleton row serializes appends so events form one ordered hash chain."""
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    last_hash = models.CharField(max_length=64, default="0" * 64)
    sequence = models.PositiveBigIntegerField(default=0)

class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    actor_label = models.CharField(max_length=150, blank=True)
    actor_id_snapshot = models.CharField(max_length=32, blank=True)
    action = models.CharField(max_length=40, db_index=True)
    document_id_text = models.CharField(max_length=36, blank=True, db_index=True)
    outcome = models.CharField(max_length=30, db_index=True)
    details = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    sequence = models.PositiveBigIntegerField(unique=True)
    previous_hash = models.CharField(max_length=64)
    event_hash = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ["-sequence"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise RuntimeError("Audit events are append-only in application code.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RuntimeError("Audit events cannot be deleted through the application model.")
