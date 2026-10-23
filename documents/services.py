from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from .models import Document, DocumentGrant
from .permissions import can_read, can_edit, can_delete
from .storage import private_storage
from .validators import inspect_upload, private_storage_key
from audit.services import record_event


def save_upload(*, actor, upload, title, category):
    info = inspect_upload(upload)
    storage = private_storage()
    key = private_storage_key(info["extension"])
    stored_name = storage.save(key, ContentFile(upload.read()))
    try:
        with transaction.atomic():
            doc = Document.objects.create(
                owner=actor, title=title.strip(), category=category.strip(),
                original_filename=info["original_filename"], storage_key=stored_name,
                content_type=info["content_type"], size_bytes=upload.size, sha256=info["sha256"])
            record_event(actor=actor, action="upload", document=doc, outcome="success")
            return doc
    except Exception:
        storage.delete(stored_name)
        raise


def update_document(*, actor, document, title, category):
    if not can_edit(actor, document):
        record_event(actor=actor, action="edit", document=document, outcome="denied")
        raise PermissionError("You are not allowed to edit this document.")
    document.title = title.strip()
    document.category = category.strip()
    document.save(update_fields=["title", "category", "updated_at"])
    record_event(actor=actor, action="edit", document=document, outcome="success")
    return document


def revoke_grant(*, actor, document, target_user):
    if not (actor.is_authenticated and actor.is_active and document.owner_id == actor.pk):
        record_event(actor=actor, action="permission_revoke", document=document, outcome="denied", details={"target_user_id": target_user.pk})
        raise PermissionError("Only the document owner can revoke this grant.")
    with transaction.atomic():
        deleted, _ = DocumentGrant.objects.filter(document=document, user=target_user).delete()
        record_event(actor=actor, action="permission_revoke", document=document, outcome="success" if deleted else "no_grant", details={"target_user_id": target_user.pk})
    return bool(deleted)


def soft_delete_document(*, actor, document):
    if not can_delete(actor, document):
        record_event(actor=actor, action="delete", document=document, outcome="denied")
        raise PermissionError("Only the document owner can delete this document.")
    document.deleted_at = timezone.now()
    document.save(update_fields=["deleted_at"])
    record_event(actor=actor, action="delete", document=document, outcome="success")
