from datetime import timedelta
from typing import Optional

from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from redis import Redis

from account.redis import redis_connection
from shortener.models import Link

from .models import Profile


def get_profile(pk) -> QuerySet:
    return get_object_or_404(Profile, pk=pk)


def get_profile_by_email(email) -> QuerySet:
    return get_object_or_404(Profile, email=email)


def get_links_by_user(
    user: Profile,
    filter_by: Optional[str] = None,
    order_by: Optional[str] = None,
) -> QuerySet:
    links = user.links.all()
    if links:
        if filter_by:
            links = links.filter(
                Q(long_link__icontains=filter_by)
                | Q(alias__icontains=filter_by)
            )
        if order_by:
            links = links.order_by(order_by)
    return links


def get_links_total_clicks(links: list[Link]) -> int:
    """Counts and returns all links clicks in list."""
    return sum(get_link_total_clicks(link.alias) for link in links)


def get_link_total_clicks(link_alias: str) -> int:
    counter = 0
    current_date = timezone.now()
    redis_con = redis_connection()
    for i in range(60):
        date = (current_date - timedelta(i)).strftime("%m.%d")
        item_key = f"{link_alias}:{date}"
        counter += redis_con.llen(item_key)

    return counter


def get_link_statistics(alias: str) -> list[tuple[str, str]]:
    current_date = timezone.now()
    redis_con = redis_connection()
    link_statistics = []
    for i in range(60):
        date = (current_date - timedelta(i)).strftime("%m.%d")
        item_key = f"{alias}:{date}"
        link_statistics.extend(iter(redis_con.lrange(item_key, 0, -1)))
    return link_statistics


def scan_redis_for_links_keys(redis_con: Redis, link_alias: str):
    return redis_con.scan(match=f"{link_alias}:*", count=60)
