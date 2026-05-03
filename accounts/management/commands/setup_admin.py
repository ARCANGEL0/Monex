import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "create / refresh the single admin user. idempotent."

    def handle(self, *args, **opts):
        User = get_user_model()
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "changeme")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"is_staff": True, "is_superuser": True},
        )
        # always force these on the single admin
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        msg = "created" if created else "refreshed"
        self.stdout.write(self.style.SUCCESS(f"admin '{username}' {msg}"))
