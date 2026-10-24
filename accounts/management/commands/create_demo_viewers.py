
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create missing TrustVault demo viewer accounts."

    def handle(self, *args, **options):
        User = get_user_model()

        viewers = [
            ("trustviewer", "BOOTSTRAP_VIEWER1_PASSWORD"),
            ("trustviewer2", "BOOTSTRAP_VIEWER2_PASSWORD"),
        ]

        for username, env_name in viewers:
            password = os.environ.get(env_name)

            if not password or len(password) < 12:
                raise CommandError(
                    f"Set {env_name} to a password of at least 12 characters."
                )

            user = User.objects.filter(username=username).first()

            if user:
                self.stdout.write(
                    f"{username} already exists; left unchanged."
                )
                continue

            user = User(username=username, role=User.Role.VIEWER)
            user.is_active = True
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f"Created viewer: {username}")
            )
