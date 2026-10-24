
from django.core.management.base import BaseCommand
from documents.models import Document


class Command(BaseCommand):
    help = "Count document records in the configured database."

    def handle(self, *args, **options):
        total = Document.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Document records in configured database: {total}"
            )
        )
