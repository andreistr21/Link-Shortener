import datetime
import json
from datetime import timedelta
from unittest import mock

from django.db.models import QuerySet
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware
from fakeredis import FakeStrictRedis

from account.redis import redis_connection
from account.selectors import get_links_total_clicks
from shortener.models import Link


class GetLinksTotalClicksTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.links_aliases = ["youtube", "youtube2"]
        cls.links = Link.objects.bulk_create(
            [
                Link(
                    long_link="https://www.youtube.com/",
                    alias=cls.links_aliases[0],
                ),
                Link(
                    long_link="https://www.youtube.com/",
                    alias=cls.links_aliases[1],
                ),
            ]
        )

    def setUp(self) -> None:
        redis_connection.cache_clear()

    def tearDown(self) -> None:
        for link in self.links:
            redis_connection().delete(
                f"{link.alias}:{make_aware(datetime.datetime(2023, 6, 19, 11, 40)).strftime('%m.%d')}"
            )

    def _get_keys_total_count_side_effect(self, keys_tuples, redis_pipeline):
        for keys_tuple in keys_tuples:
            key_list = keys_tuple[1]
            for key in key_list:
                redis_pipeline.llen(key)

    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 19, 11, 40)
    )
    @mock.patch("account.selectors.get_keys_total_count")
    @mock.patch("account.redis.from_url", FakeStrictRedis)
    def test_not_empty_lists(self, get_keys_total_count_mock, _):
        expected_clicks_amount = 10
        redis_conn = redis_connection()

        get_keys_total_count_mock.side_effect = (
            self._get_keys_total_count_side_effect
        )

        # Adds `clicks_amount` clicks for links
        for link in self.links:
            for i in range(expected_clicks_amount):
                redis_conn.lpush(
                    f"{link.alias}:{timezone.now().strftime('%m.%d')}",
                    json.dumps(
                        {
                            "time": (
                                timezone.now() + timedelta(minutes=i)
                            ).isoformat(),
                            "country": "PL",
                        }
                    ),
                )

        clicks_amount_1 = get_links_total_clicks(
            Link.objects.filter(pk=self.links[0].pk)
        )
        clicks_amount_2 = get_links_total_clicks(
            Link.objects.filter(pk=self.links[1].pk)
        )

        self.assertEqual(clicks_amount_1, expected_clicks_amount)
        self.assertEqual(clicks_amount_2, expected_clicks_amount)

    @mock.patch("account.selectors.get_keys_total_count")
    @mock.patch("account.redis.from_url", FakeStrictRedis)
    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 19, 11, 40)
    )
    def test_return_empty_lists(self, _, get_keys_total_count_mock):
        get_keys_total_count_mock.side_effect = (
            self._get_keys_total_count_side_effect
        )

        clicks_amount_1 = get_links_total_clicks(
            Link.objects.filter(pk=self.links[0].pk)
        )
        clicks_amount_2 = get_links_total_clicks(
            Link.objects.filter(pk=self.links[1].pk)
        )

        self.assertEqual(clicks_amount_1, 0)
        self.assertEqual(clicks_amount_2, 0)
