from django.contrib import admin
from .models import AuditChainState, AuditEvent

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("sequence", "timestamp", "actor_label", "action", "outcome", "document_id_text")
    list_filter = ("action", "outcome")
    readonly_fields = [field.name for field in AuditEvent._meta.fields]
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(AuditChainState)
class AuditChainStateAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "last_hash", "sequence")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
