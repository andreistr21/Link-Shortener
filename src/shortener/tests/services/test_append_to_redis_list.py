import datetime
import json
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from fakeredis import FakeStrictRedis

from shortener.redis import redis_connection
from shortener.services import append_to_redis_list


class AppendToRedisListTests(TestCase):
    @mock.patch("shortener.redis.Redis", FakeStrictRedis)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 23, 18, 20)
    )
    def test_append_to_redis_list(self, _):
        alias = "test-alias"
        country_code = "PL"
        append_to_redis_list(alias, country_code)
        redis_con = redis_connection()

        self.assertEqual(
            redis_con.lrange(alias, 0, 1)[0],
            bytes(
                json.dumps(
                    {"time": timezone.now().isoformat(), "country": "PL"}
                ),
                "utf-8",
            ),
        )
