from datetime import timedelta
from typing import Optional

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from redis import Redis
from redis.client import Pipeline

from account.redis import redis_connection
from shortener.models import Link

from .models import Profile


def get_profile(pk) -> Profile:
    return get_object_or_404(Profile, pk=pk)


def get_profile_by_email(email) -> Profile:
    return get_object_or_404(Profile, email=email)


def get_links_by_user(
    user: Profile | AbstractBaseUser | AnonymousUser,
    filter_by: Optional[str] = None,
    order_by: Optional[str] = None,
) -> QuerySet[Link]:
    links = user.links.all()  # type: ignore
    if links:
        if filter_by:
            links = links.filter(
                Q(long_link__icontains=filter_by)
                | Q(alias__icontains=filter_by)
            )
        if order_by:
            links = links.order_by(order_by)
    return links


# 306ms, 226ms
# TODO: update tests
def get_links_total_clicks(links: QuerySet[Link]) -> int:
    """Counts and returns all links clicks in list."""
    redis_con = redis_connection()

    with redis_con.pipeline() as redis_pipeline:
        for link in links:
            redis_pipeline.scan(match=f"{link.alias}:*", count=60)

        keys_tuples = redis_pipeline.execute()

    with redis_con.pipeline() as redis_pipeline:
        get_keys_total_count(keys_tuples, redis_pipeline)  # type: ignore
        total_clicks = sum(redis_pipeline.execute())

    return total_clicks


# TODO: add tests
def get_keys_total_count(
    keys_tuples: list[tuple[int, list[bytes]]], redis_pipeline: Pipeline
) -> None:
    for keys_tuple in keys_tuples:
        key_list = keys_tuple[1]
        for key in key_list:
            key_dec = key.decode(encoding="utf8")
            redis_pipeline.llen(key_dec)


def get_link_total_clicks(link_alias: str) -> int:
    counter = 0
    current_date = timezone.now()
    redis_con = redis_connection()
    for i in range(60):
        date = (current_date - timedelta(i)).strftime("%m.%d")
        item_key = f"{link_alias}:{date}"
        counter += redis_con.llen(item_key)

    return counter


def get_link_statistics(alias: str) -> list[bytes]:
    current_date = timezone.now()
    redis_con = redis_connection()
    link_statistics = []
    for i in range(60):
        date = (current_date - timedelta(i)).strftime("%m.%d")
        item_key = f"{alias}:{date}"
        link_statistics.extend(iter(redis_con.lrange(item_key, 0, -1)))
    return link_statistics


def scan_redis_for_links_keys(
    redis_con: Redis, link_alias: str
) -> tuple[int, list[bytes]]:
    return redis_con.scan(match=f"{link_alias}:*", count=60)
