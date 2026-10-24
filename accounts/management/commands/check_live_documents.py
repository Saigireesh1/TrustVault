
from django.core.management.base import BaseCommand
from documents.models import Document


class Command(BaseCommand):
    help = "Temporarily count TrustVault documents in the configured database."

    def handle(self, *args, **options):
        total = Document.objects.count()
        self.stdout.write(f"Document records in configured database: {total}")

        for document in Document.objects.all()[:10]:
            self.stdout.write(f"- {document.title}")
