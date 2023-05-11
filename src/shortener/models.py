from django.db import models

from account.models import Profile


class Link(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    long_link = models.CharField(max_length=2000)
    short_link = models.CharField(max_length=250, null=True, blank=True)

    # TODO: Add index by user, long link and short link. Add created data field
