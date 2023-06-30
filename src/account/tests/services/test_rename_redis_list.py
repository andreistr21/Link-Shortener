from unittest import mock
from django.test import TestCase
from fakeredis import FakeStrictRedis
from account.redis import redis_connection

from account.services import rename_redis_list


class RenameRedisListTests(TestCase):
    @mock.patch("account.redis.Redis", return_value=FakeStrictRedis())
    def test_key_renamed(self, _):
        redis_con = redis_connection()
        redis_con.lpush("test-alias", "test-value")
        rename_redis_list("test-alias", "new-test-alias")

        self.assertFalse(redis_con.lrange("test-alias", 0, -1))
        self.assertEqual(
            redis_con.lrange("new-test-alias", 0, -1),
            ["test-value".encode("utf-8")],
        )

    @mock.patch("account.redis.Redis", return_value=FakeStrictRedis())
    def test_if_not_such_key_exists(self, _):
        redis_con = redis_connection()
        rename_redis_list("test-alias", "new-test-alias")

        self.assertFalse(redis_con.exists("new-test-alias"))
