
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Temporarily repair the TrustVault owner login."

    def handle(self, *args, **options):
        username = os.environ.get("BOOTSTRAP_ADMIN_USERNAME")
        password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD")

        if username != "saigireesh":
            raise CommandError("Invalid bootstrap username.")

        if not password or len(password) < 12:
            raise CommandError("Set a password of at least 12 characters.")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "role": User.Role.OWNER,
                "is_active": True,
            },
        )

        user.role = User.Role.OWNER
        user.is_active = True
        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS("TrustVault owner login repaired.")
        )
