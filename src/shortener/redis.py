from functools import lru_cache
from os import getenv

from redis import Redis


@lru_cache(maxsize=1)
def redis_connection() -> Redis:
    """Creates redis connection during first call and returns it. During next
    call cached value will be returned"""
    return Redis(host=getenv("REDIS_HOST"), port="6379")
