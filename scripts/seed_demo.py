"""Seed demo accounts: run with `python manage.py shell < scripts/seed_demo.py`.
Change all demo passwords before any public deployment. Do not reuse these passwords.
"""
from accounts.models import User
from documents.models import Document
from documents.services import save_upload
from django.core.files.uploadedfile import SimpleUploadedFile

DEMO_PASSWORD = "Demo-Only-Change-Me-123!"
for username, role in [("tv_admin", User.Role.ADMIN), ("tv_owner", User.Role.OWNER), ("tv_viewer", User.Role.VIEWER), ("tv_other", User.Role.VIEWER)]:
    user, created = User.objects.get_or_create(username=username, defaults={"role": role, "email": f"{username}@example.test"})
    if created:
        user.set_password(DEMO_PASSWORD)
        user.save()
    print(f"{username}: {'created' if created else 'already exists'} (role={user.role})")
owner = User.objects.get(username="tv_owner")
if not Document.objects.filter(owner=owner, title="Demo policy document").exists():
    upload = SimpleUploadedFile("demo.txt", b"TrustVault demo file. Replace this seed content.", content_type="text/plain")
    save_upload(actor=owner, upload=upload, title="Demo policy document", category="Demo")
print("Seed complete. Demo password is for local evaluation only; change it before deployment.")
