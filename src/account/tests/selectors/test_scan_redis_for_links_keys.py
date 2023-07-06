import datetime
from functools import lru_cache
import json
from unittest import mock
from django.test import TestCase
from fakeredis import FakeStrictRedis
from django.utils.timezone import make_aware
from django.utils import timezone

from account.selectors import scan_redis_for_links_keys
from shortener.models import Link


class ScanRedisForLinksKeysTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.link = Link.objects.create(
            long_link="https://www.youtube.com/", alias="youtube"
        )

    def tearDown(self) -> None:
        self._redis_connection().delete(
            f"{self.link.alias}:{make_aware(datetime.datetime(2023, 6, 23, 18, 20)).strftime('%m.%d')}"
        )

    @lru_cache(maxsize=1)
    def _redis_connection(self) -> FakeStrictRedis:
        """Creates redis connection during first call and returns it. During
        next call cached value will be returned"""
        return FakeStrictRedis()

    def test_return_empty_list(self):
        redis_con = self._redis_connection()

        _, keys = scan_redis_for_links_keys(redis_con, self.link.alias)

        self.assertFalse(keys)

    @mock.patch.object(
        timezone,
        "now",
        return_value=make_aware(datetime.datetime(2023, 6, 23, 18, 20)),
    )
    def test_return_not_empty_list(self, _):
        clicks = [
            json.dumps({"time": "date", "country": "PL"}),
            json.dumps({"time": "date", "country": "PL"}),
            json.dumps({"time": "date", "country": "PL"}),
            json.dumps({"time": "date", "country": "PL"}),
            json.dumps({"time": "date", "country": "PL"}),
        ]
        redis_con = self._redis_connection()
        for el in clicks:
            redis_con.lpush(
                f'{self.link.alias}:{timezone.now().strftime("%m.%d")}',
                str(el),
            )

        _, keys = scan_redis_for_links_keys(redis_con, self.link.alias)

        self.assertEqual(keys, [b"youtube:06.23"])
