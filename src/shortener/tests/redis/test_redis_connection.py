from unittest import mock

from django.test import TestCase

from shortener.redis import redis_connection


class RedisConnection(TestCase):
    @mock.patch("shortener.redis.Redis")
    def test_redis_connection_caching(self, redis_mock):
        connection1 = redis_connection()
        connection2 = redis_connection()

        redis_mock.assert_called_once_with(host="127.0.0.1", port="6379")
        self.assertEqual(connection1, connection2)
