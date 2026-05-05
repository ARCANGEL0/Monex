import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone


class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(secrets.randbelow(900000) + 100000)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.used and timezone.now() <= self.expires_at

    @classmethod
    def verify(cls, email, code):
        try:
            entry = cls.objects.filter(
                email=email, code=str(code), used=False,
                expires_at__gte=timezone.now(),
            ).latest("created_at")
            entry.used = True
            entry.save(update_fields=["used"])
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def generate_for(cls, email):
        return cls.objects.create(email=email)
