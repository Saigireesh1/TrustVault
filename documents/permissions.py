from .models import Document, DocumentGrant

def can_read(user, document):
    """Authoritative policy: owner or an active explicit read/edit grant.

    Admin role does not imply access to confidential content. A superuser can
    administer the app but must still be granted document access by this policy.
    """
    if not user.is_authenticated or not user.is_active or document.deleted_at is not None:
        return False
    if document.owner_id == user.pk:
        return True
    return DocumentGrant.objects.filter(document=document, user=user, permission__in=["read", "edit"]).exists()

def can_edit(user, document):
    if not user.is_authenticated or not user.is_active or document.deleted_at is not None:
        return False
    if document.owner_id == user.pk:
        return True
    return DocumentGrant.objects.filter(document=document, user=user, permission="edit").exists()

def can_delete(user, document):
    return bool(user.is_authenticated and user.is_active and document.deleted_at is None and document.owner_id == user.pk)

def can_manage_grants(user, document):
    return bool(user.is_authenticated and user.is_active and document.deleted_at is None and document.owner_id == user.pk)
