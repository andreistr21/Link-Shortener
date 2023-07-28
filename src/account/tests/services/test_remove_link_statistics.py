from functools import lru_cache
from unittest import mock

from django.test import TestCase
from fakeredis import FakeStrictRedis
from redis import Redis
from account.services import remove_link_statistics

from shortener.models import Link
from shorty.settings import REDIS_TTL


class RemoveLinkStatisticsTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.link = Link.objects.create(
            long_link="http://www.youtube.com/", alias="youtube"
        )

    @lru_cache(maxsize=1)
    def _redis_connection(self) -> Redis:
        """Creates redis connection during first call and returns it. During
        next call cached value will be returned"""
        return FakeStrictRedis()

    @mock.patch(
        "account.services.scan_redis_for_links_keys", return_value=(None, [])
    )
    @mock.patch("account.services.redis_connection")
    def test_if_data_do_not_exists(self, redis_connection_mock, _):
        redis_connection_mock.return_value = self._redis_connection()
        redis_con = self._redis_connection()

        _, keys_1 = list(
            redis_con.scan(match=f"{self.link.alias}:*", count=60)
        )
        self.assertFalse(keys_1)
        remove_link_statistics(self.link.alias)
        _, keys_2 = list(
            redis_con.scan(match=f"{self.link.alias}:*", count=60)
        )
        self.assertFalse(keys_2)

    @mock.patch("account.services.scan_redis_for_links_keys")
    @mock.patch("account.services.redis_connection")
    def test_if_data_exists(
        self, redis_connection_mock, scan_redis_for_links_keys_mock
    ):
        redis_connection_mock.return_value = self._redis_connection()
        scan_redis_for_links_keys_mock.return_value = (
            None,
            [f"{self.link.alias}:07.07", f"{self.link.alias}:07.06"],
        )
        redis_con = self._redis_connection()
        redis_con.lpush(f"{self.link.alias}:07.07", "test-data")
        redis_con.lpush(f"{self.link.alias}:07.07", "test-data2")
        redis_con.lpush(f"{self.link.alias}:07.07", "test-data3")
        redis_con.lpush(f"{self.link.alias}:07.06", "test-data")
        redis_con.lpush(f"{self.link.alias}:07.06", "test-data2")

        _, keys_1 = list(
            redis_con.scan(match=f"{self.link.alias}:*", count=60)
        )
        self.assertEqual(len(keys_1), 2)
        remove_link_statistics(self.link.alias)
        _, keys_2 = list(
            redis_con.scan(match=f"{self.link.alias}:*", count=60)
        )
        self.assertFalse(keys_2)
