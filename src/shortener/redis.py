from functools import lru_cache

from redis import Redis


# TODO: add tests
@lru_cache(maxsize=1)
def redis_connection() -> Redis:
    """Creates redis connection during first call and returns it. During next
    call cached value will be returned"""
    return Redis(host="127.0.0.1", port="6379")
