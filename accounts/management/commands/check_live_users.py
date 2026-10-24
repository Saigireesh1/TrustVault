
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Safely list live TrustVault usernames and roles."

    def handle(self, *args, **options):
        User = get_user_model()

        users = User.objects.order_by("username").values_list(
            "username", "role", "is_active"
        )

        self.stdout.write("Live TrustVault accounts:")
        for username, role, is_active in users:
            self.stdout.write(
                f"username={username}, role={role}, active={is_active}"
            )
