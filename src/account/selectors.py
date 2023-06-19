from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from account.redis import redis_connection
from shortener.models import Link

from .models import Profile


def get_profile(pk):
    return get_object_or_404(Profile, pk=pk)


def get_profile_by_email(email):
    return get_object_or_404(Profile, email=email)


def get_links_by_user(user: Profile) -> QuerySet:
    return user.links.all()


# TODO: add tests
def get_account_total_clicks(links: list[Link]) -> int:
    """Counts and returns all clicks on user links."""
    return sum(redis_connection().llen(link.alias) for link in links)


# TODO: add tests
def get_link_total_clicks(link_alias: str) -> int:
    return redis_connection().llen(link_alias)
