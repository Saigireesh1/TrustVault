
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Read-only check of TrustVault login account status."

    def handle(self, *args, **options):
        User = get_user_model()

        for username in ("saigireesh", "trustviewer", "trustviewer2"):
            user = User.objects.filter(username=username).first()

            if user is None:
                self.stdout.write(f"{username}: MISSING")
                continue

            self.stdout.write(
                f"{username}: "
                f"active={user.is_active}, "
                f"role={user.role}, "
                f"password_usable={user.has_usable_password()}, "
                f"password_algorithm="
                f"{user.password.split('$', 1)[0] if user.password else 'EMPTY'}"
            )
