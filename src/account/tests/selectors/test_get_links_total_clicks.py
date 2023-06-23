import datetime
import json
from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from fakeredis import FakeStrictRedis
from account.redis import redis_connection

from account.selectors import get_links_total_clicks
from shortener.models import Link


class GetLinksTotalClicksTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.links = Link.objects.bulk_create(
            [
                Link(long_link="https://www.youtube.com/", alias="youtube"),
                Link(long_link="https://www.youtube.com/", alias="youtube2"),
            ]
        )

    def tearDown(self) -> None:
        for link in self.links:
            redis_connection().delete(link.alias)

    @mock.patch("account.redis.Redis", FakeStrictRedis)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 19, 11, 40)
    )
    def test_not_empty_lists(self, _):
        clicks_amount = 10
        redis_conn = redis_connection()

        # Adds `clicks_amount` clicks for links
        for link in self.links:
            for i in range(clicks_amount):
                redis_conn.lpush(
                    link.alias,
                    json.dumps(
                        {
                            "time": (
                                timezone.now() + timedelta(minutes=i)
                            ).isoformat(),
                            "country": "PL",
                        }
                    ),
                )

        clicks_amount_1 = get_links_total_clicks([self.links[0]])
        clicks_amount_2 = get_links_total_clicks([self.links[1]])

        self.assertEqual(clicks_amount, clicks_amount_1)
        self.assertEqual(clicks_amount, clicks_amount_2)

    @mock.patch("account.redis.Redis", FakeStrictRedis)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 19, 11, 40)
    )
    def test_return_empty_lists(self, _):
        clicks_amount_1 = get_links_total_clicks([self.links[0]])
        clicks_amount_2 = get_links_total_clicks([self.links[1]])

        self.assertEqual(0, clicks_amount_1)
        self.assertEqual(0, clicks_amount_2)
