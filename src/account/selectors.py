from typing import Optional

from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from account.redis import redis_connection
from shortener.models import Link

from .models import Profile


def get_profile(pk):
    return get_object_or_404(Profile, pk=pk)


def get_profile_by_email(email):
    return get_object_or_404(Profile, email=email)


# TODO: update tests
def get_links_by_user(
    user: Profile,
    filter_by: Optional[str] = None,
    order_by: Optional[str] = None,
) -> QuerySet:
    links = user.links.all()
    if filter_by:
        links = links.filter(
            Q(long_link__icontains=filter_by) | Q(alias__icontains=filter_by)
        )
    if order_by:
        links = links.order_by(order_by)
    return links


def get_links_total_clicks(links: list[Link]) -> int:
    """Counts and returns all links clicks in list."""
    return sum(get_link_total_clicks(link.alias) for link in links)


def get_link_total_clicks(link_alias: str) -> int:
    return redis_connection().llen(link_alias)
