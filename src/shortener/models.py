from django.contrib.auth.models import User
from django.db import models
from django.forms import CharField

from account.models import Profile


class Link(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    
    long_link = CharField(max_length=2000)
    short_link = CharField(max_length=250)
