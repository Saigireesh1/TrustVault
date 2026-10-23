from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Files live outside static/ and are never exposed by a public URL route.
def private_storage():
    location = Path(settings.MEDIA_ROOT)
    location.mkdir(parents=True, exist_ok=True)
    return FileSystemStorage(location=location, base_url=None)
