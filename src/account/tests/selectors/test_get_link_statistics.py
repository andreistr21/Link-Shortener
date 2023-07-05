import json
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from fakeredis import FakeStrictRedis

from account.redis import redis_connection
from account.selectors import get_link_statistics


class GetLinkStatistics(TestCase):
    @mock.patch("account.redis.Redis", FakeStrictRedis)
    def test_if_no_such_lists_exists(self):
        resp = get_link_statistics("test-alias")

        self.assertEqual(len(resp), 0)

    @mock.patch("account.redis.Redis", FakeStrictRedis)
    def test_if_such_list_exists(self):
        redis_con = redis_connection()
        clicks = [
            json.dumps({"time": "date", "country": "PL"}),
            json.dumps({"time": "date", "country": "PL"}),
            json.dumps({"time": "date", "country": "PL"}),
            json.dumps({"time": "date", "country": "PL"}),
            json.dumps({"time": "date", "country": "PL"}),
        ]
        alias = "test-alias2"
        for el in clicks:
            redis_con.lpush(
                f'{alias}:{timezone.now().strftime("%m.%d")}', str(el)
            )
        resp = get_link_statistics(alias)
        new_resp = [el.decode("utf-8") for el in resp]

        self.assertEqual(new_resp, clicks)
