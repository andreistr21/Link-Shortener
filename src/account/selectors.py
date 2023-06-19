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


def get_links_total_clicks(links: list[Link]) -> int:
    """Counts and returns all links clicks in list."""
    return sum(get_link_total_clicks(link.alias) for link in links)


def get_link_total_clicks(link_alias: str) -> int:
    return redis_connection().llen(link_alias)
