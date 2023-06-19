from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from .models import Profile


def get_profile(pk):
    return get_object_or_404(Profile, pk=pk)


def get_profile_by_email(email):
    return get_object_or_404(Profile, email=email)


# TODO: add tests
def get_links_by_user(user: Profile) -> QuerySet:
    return user.links.all()
