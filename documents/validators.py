import hashlib
import os
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError

# Deliberately small allowlist for the hackathon build. Expand only with tests.
ALLOWED_TYPES = {
    ".pdf": ("application/pdf",),
    ".txt": ("text/plain",),
    ".png": ("image/png",),
    ".jpg": ("image/jpeg",),
    ".jpeg": ("image/jpeg",),
}

def inspect_upload(upload):
    name = os.path.basename(upload.name or "upload")
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_TYPES:
        raise ValidationError("Unsupported file extension. Allowed: PDF, TXT, PNG, JPG.")
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if upload.size <= 0 or upload.size > max_bytes:
        raise ValidationError(f"File must be between 1 byte and {settings.MAX_UPLOAD_MB} MB.")
    # Read bytes to verify basic signatures, then rewind for storage.
    head = upload.read(16)
    upload.seek(0)
    signatures = {
        ".pdf": head.startswith(b"%PDF-"),
        ".png": head.startswith(b"\x89PNG\r\n\x1a\n"),
        ".jpg": head.startswith(b"\xff\xd8\xff"),
        ".jpeg": head.startswith(b"\xff\xd8\xff"),
        ".txt": b"\x00" not in head,
    }
    if not signatures[ext]:
        raise ValidationError("File content does not match its extension.")
    digest = hashlib.sha256()
    for chunk in upload.chunks():
        digest.update(chunk)
    upload.seek(0)
    mime = ALLOWED_TYPES[ext][0]
    return {"original_filename": name[:255], "extension": ext, "sha256": digest.hexdigest(), "content_type": mime}

def private_storage_key(extension):
    return f"{uuid.uuid4().hex}{extension}"
