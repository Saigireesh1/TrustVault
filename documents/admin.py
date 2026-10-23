from django.contrib import admin
from .models import Document, DocumentGrant, DocumentVersion

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "category", "created_at", "deleted_at")
    search_fields = ("title", "original_filename", "owner__username")
    readonly_fields = ("storage_key", "sha256", "size_bytes", "created_at", "updated_at")

@admin.register(DocumentGrant)
class DocumentGrantAdmin(admin.ModelAdmin):
    list_display = ("document", "user", "permission", "granted_by", "created_at")
    readonly_fields = ("document", "user", "permission", "granted_by", "created_at")

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("document", "version_number", "created_by", "created_at")
    readonly_fields = [field.name for field in DocumentVersion._meta.fields]
