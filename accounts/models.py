from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        OWNER = "OWNER", "Document owner"
        VIEWER = "VIEWER", "Viewer"
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.VIEWER)

    @property
    def is_trustvault_admin(self):
        return self.is_superuser or self.role == self.Role.ADMIN
