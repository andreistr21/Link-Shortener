import datetime
from functools import lru_cache
import json
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from fakeredis import FakeStrictRedis

from shortener.services import redis_connection
from shortener.services import append_to_redis_list


@lru_cache(maxsize=1)
def fake_redis_connection():
    """Creates redis connection during first call and returns it. During next
    call cached value will be returned"""
    return FakeStrictRedis()


class AppendToRedisListTests(TestCase):
    @mock.patch("shortener.services.redis_connection", fake_redis_connection)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 23, 18, 20)
    )
    def test_append_to_redis_list(self, _):
        alias = "test-alias"
        country_code = "PL"
        append_to_redis_list(alias, country_code)
        redis_con = fake_redis_connection()

        self.assertEqual(
            redis_con.lrange(alias, 0, 1)[0],
            bytes(
                json.dumps(
                    {"time": timezone.now().isoformat(), "country": "PL"}
                ),
                "utf-8",
            ),
        )
