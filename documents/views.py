
import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import UploadDocumentForm, DocumentEditForm, GrantForm
from .models import Document, DocumentGrant
from .permissions import can_read, can_edit, can_delete, can_manage_grants
from .services import (
    save_upload,
    update_document,
    revoke_grant,
    soft_delete_document,
)
from .storage import private_storage
from audit.services import record_event

User = get_user_model()


def accessible_documents(user):
    # Only return non-deleted documents the user owns or can access.
    return Document.objects.filter(
        deleted_at__isnull=True
    ).filter(
        Q(owner=user)
        | Q(
            grants__user=user,
            grants__permission__in=["read", "edit"],
        )
    ).distinct()


@login_required
@require_http_methods(["GET", "POST"])
def document_list(request):
    if request.method == "POST":
        form = UploadDocumentForm(request.POST, request.FILES)

        if form.is_valid():
            if (
                request.user.role not in [User.Role.OWNER, User.Role.ADMIN]
                and not request.user.is_superuser
            ):
                record_event(
                    actor=request.user,
                    action="upload",
                    outcome="denied",
                )
                return HttpResponseForbidden(
                    "Your role cannot upload documents."
                )

            try:
                doc = save_upload(
                    actor=request.user,
                    upload=form.cleaned_data["file"],
                    title=form.cleaned_data["title"],
                    category=form.cleaned_data["category"],
                )
            except ValidationError as exc:
                record_event(
                    actor=request.user,
                    action="upload",
                    outcome="denied",
                    details={"reason": "validation_failed"},
                )
                form.add_error("file", exc)
            else:
                messages.success(
                    request,
                    "Document uploaded securely.",
                )
                return redirect("documents:detail", pk=doc.pk)
    else:
        form = UploadDocumentForm()

    docs = accessible_documents(request.user)

    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    owner = request.GET.get("owner", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    # Apply search and filters to the document list.
    if q:
        docs = docs.filter(
            Q(title__icontains=q)
            | Q(original_filename__icontains=q)
        )

    if category:
        docs = docs.filter(category__icontains=category)

    if owner:
        docs = docs.filter(
            Q(owner__username__icontains=owner)
            | Q(owner__email__icontains=owner)
        )

    if date_from:
        docs = docs.filter(created_at__date__gte=date_from)

    if date_to:
        docs = docs.filter(created_at__date__lte=date_to)

    # NEW FEATURE: Count all accessible, non-deleted documents.
    # This count is independent of the search filters above.
    document_count = accessible_documents(request.user).count()

    return render(
        request,
        "documents/list.html",
        {
            "documents": docs,
            "form": form,
            "q": q,
            "category": category,
            "owner": owner,
            "date_from": date_from,
            "date_to": date_to,
            "document_count": document_count,
        },
    )


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(
        Document,
        pk=pk,
        deleted_at__isnull=True,
    )

    if not can_read(request.user, doc):
        record_event(
            actor=request.user,
            action="read_metadata",
            document=doc,
            outcome="denied",
        )
        return HttpResponseForbidden(
            "You do not have access to this document."
        )

    record_event(
        actor=request.user,
        action="read_metadata",
        document=doc,
        outcome="success",
    )

    grants = (
        doc.grants.select_related("user", "granted_by")
        if doc.owner_id == request.user.pk
        else []
    )

    return render(
        request,
        "documents/detail.html",
        {
            "document": doc,
            "grants": grants,
            "can_edit": can_edit(request.user, doc),
            "can_manage_grants": can_manage_grants(
                request.user, doc
            ),
            "grant_form": GrantForm(),
        },
    )


@login_required
@require_POST
def document_download(request, pk):
    doc = get_object_or_404(
        Document,
        pk=pk,
        deleted_at__isnull=True,
    )

    # Security check: only authorized users can download.
    if not can_read(request.user, doc):
        record_event(
            actor=request.user,
            action="download",
            document=doc,
            outcome="denied",
        )
        return HttpResponseForbidden(
            "You do not have access to this document."
        )

    storage = private_storage()

    if not storage.exists(doc.storage_key):
        record_event(
            actor=request.user,
            action="download",
            document=doc,
            outcome="storage_missing",
        )
        raise Http404("File not found.")

    record_event(
        actor=request.user,
        action="download",
        document=doc,
        outcome="success",
    )

    handle = storage.open(doc.storage_key, "rb")

    response = FileResponse(
        handle,
        as_attachment=True,
        filename=Path(doc.original_filename).name,
        content_type=doc.content_type,
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "no-store, private"

    return response


@login_required
@require_http_methods(["GET", "POST"])
def document_edit(request, pk):
    doc = get_object_or_404(
        Document,
        pk=pk,
        deleted_at__isnull=True,
    )

    if not can_edit(request.user, doc):
        record_event(
            actor=request.user,
            action="edit",
            document=doc,
            outcome="denied",
        )
        return HttpResponseForbidden(
            "You do not have edit access."
        )

    form = DocumentEditForm(
        request.POST or None,
        instance=doc,
    )

    if request.method == "POST" and form.is_valid():
        try:
            update_document(
                actor=request.user,
                document=doc,
                title=form.cleaned_data["title"],
                category=form.cleaned_data["category"],
            )
        except PermissionError:
            return HttpResponseForbidden(
                "You do not have edit access."
            )

        messages.success(
            request,
            "Document details updated.",
        )
        return redirect("documents:detail", pk=doc.pk)

    return render(
        request,
        "documents/edit.html",
        {
            "form": form,
            "document": doc,
        },
    )


@login_required
@require_POST
def document_delete(request, pk):
    doc = get_object_or_404(
        Document,
        pk=pk,
        deleted_at__isnull=True,
    )

    if not can_delete(request.user, doc):
        record_event(
            actor=request.user,
            action="delete",
            document=doc,
            outcome="denied",
        )
        return HttpResponseForbidden(
            "Only the owner can delete this document."
        )

    soft_delete_document(
        actor=request.user,
        document=doc,
    )

    messages.success(
        request,
        "Document moved to deleted state.",
    )
    return redirect("documents:list")


@login_required
@require_POST
def grant_access(request, pk):
    doc = get_object_or_404(
        Document,
        pk=pk,
        deleted_at__isnull=True,
    )

    if not can_manage_grants(request.user, doc):
        record_event(
            actor=request.user,
            action="permission_grant",
            document=doc,
            outcome="denied",
        )
        return HttpResponseForbidden(
            "Only the owner can grant access."
        )

    form = GrantForm(request.POST)

    if not form.is_valid():
        messages.error(
            request,
            "Please choose a valid user and permission.",
        )
        return redirect("documents:detail", pk=doc.pk)

    target = form.cleaned_data["user"]

    if target.pk == doc.owner_id:
        messages.error(
            request,
            "The owner already has access.",
        )
        return redirect("documents:detail", pk=doc.pk)

    if target.role == User.Role.ADMIN or target.is_superuser:
        # Admins can receive explicit grants like any other named user.
        pass

    grant, created = DocumentGrant.objects.update_or_create(
        document=doc,
        user=target,
        defaults={
            "permission": form.cleaned_data["permission"],
            "granted_by": request.user,
        },
    )

    record_event(
        actor=request.user,
        action="permission_grant",
        document=doc,
        outcome="success",
        details={
            "target_user_id": target.pk,
            "permission": grant.permission,
            "created": created,
        },
    )

    messages.success(
        request,
        f"Access updated for {target.username}.",
    )
    return redirect("documents:detail", pk=doc.pk)


@login_required
@require_POST
def revoke_access(request, pk, user_id):
    doc = get_object_or_404(
        Document,
        pk=pk,
        deleted_at__isnull=True,
    )
    target = get_object_or_404(User, pk=user_id)

    try:
        removed = revoke_grant(
            actor=request.user,
            document=doc,
            target_user=target,
        )
    except PermissionError:
        return HttpResponseForbidden(
            "Only the owner can revoke access."
        )

    messages.success(
        request,
        "Access revoked." if removed
        else "No active grant existed.",
    )
    return redirect("documents:detail", pk=doc.pk)
