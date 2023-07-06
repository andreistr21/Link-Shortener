import datetime
import json
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware
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
        redis_connection().delete(
            f"{self.link.alias}:{make_aware(datetime.datetime(2023, 6, 19, 11, 40)).strftime('%m.%d')}"
        )

    @mock.patch("account.redis.Redis", FakeStrictRedis)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 19, 11, 40)
    )
    def test_not_empty_lists(self, _):
        expected_clicks_amount = 10
        redis_conn = redis_connection()

        # Adds "expected_clicks_amount" clicks for links
        for i in range(expected_clicks_amount):
            redis_conn.lpush(
                f'{self.link.alias}:{timezone.now().strftime("%m.%d")}',
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

        self.assertEqual(clicks_amount, expected_clicks_amount)

    @mock.patch("account.redis.Redis", FakeStrictRedis)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 19, 11, 40)
    )
    def test_if_lists_are_empty(self, _):
        clicks_amount = get_link_total_clicks(self.link.alias)

        self.assertEqual(0, clicks_amount)
