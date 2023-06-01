from django.db import models

from account.models import Profile


class Link(models.Model):
    user_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True
    )

    long_link = models.TextField(max_length=2000)
    alias = models.CharField(max_length=80, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["long_link"]),
            models.Index(fields=["alias"]),
        ]
