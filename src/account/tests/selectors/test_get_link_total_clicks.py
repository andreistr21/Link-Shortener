import datetime
import json
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from fakeredis import FakeStrictRedis

from account.redis import redis_connection
from account.selectors import get_link_total_clicks
from shortener.models import Link


class GetLinkTotalClicksTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.link = Link.objects.create(
            long_link="https://www.youtube.com/", alias="youtube"
        )

    def tearDown(self) -> None:
        redis_connection().delete(self.link.alias)

    @mock.patch("account.redis.Redis", FakeStrictRedis)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 19, 11, 40)
    )
    def test_not_empty_lists(self, _):
        clicks_amount = 10
        redis_conn = redis_connection()

        # Adds `clicks_amount` clicks for links
        for i in range(clicks_amount):
            redis_conn.lpush(
                self.link.alias,
                json.dumps(
                    {
                        "time": (
                            timezone.now() + datetime.timedelta(minutes=i)
                        ).isoformat(),
                        "country": "PL",
                    }
                ),
            )

        clicks_amount = get_link_total_clicks(self.link.alias)

        self.assertEqual(clicks_amount, clicks_amount)

    @mock.patch("account.redis.Redis", FakeStrictRedis)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 19, 11, 40)
    )
    def test_return_empty_lists(self, _):
        clicks_amount = get_link_total_clicks(self.link.alias)

        self.assertEqual(0, clicks_amount)
