from os import environ
from unittest import mock

from django.test import TestCase

from account.redis import redis_connection


class RedisConnectionTests(TestCase):
    def setUp(self) -> None:
        redis_connection.cache_clear()
    
    @mock.patch("account.redis.from_url")
    def test_redis_non_TSL_connection_caching(self, redis_mock):
        REDIS_URL = "redis_non_TSL_link"
        environ["REDIS_URL"] = REDIS_URL
        connection1 = redis_connection()
        connection2 = redis_connection()

        redis_mock.assert_called_once_with(REDIS_URL)
        self.assertEqual(connection1, connection2)

    @mock.patch("account.redis.from_url")
    def test_redis_TSL_connection_caching(self, redis_mock):
        REDIS_URL = "rediss://:redis_TSL_link"
        environ["REDIS_URL"] = REDIS_URL
        connection1 = redis_connection()
        connection2 = redis_connection()

        redis_mock.assert_called_once_with(REDIS_URL, ssl_cert_reqs=None)
        self.assertEqual(connection1, connection2)
