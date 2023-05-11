from django.conf import settings
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    last_online = models.DateField()

    @property
    def update_last_online(self) -> None:
        self.last_online = timezone.now()
        self.save()
