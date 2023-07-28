from unittest import mock

from django.test import TestCase
from fakeredis import FakeStrictRedis

from account.redis import redis_connection
from account.services import construct_redis_key, rename_redis_list


class RenameRedisListTests(TestCase):
    def setUp(self) -> None:
        redis_connection.cache_clear()

    @mock.patch("account.redis.from_url", FakeStrictRedis)
    def test_key_renamed(self):
        redis_con = redis_connection()
        old_key = construct_redis_key("test-alias", "07.27")
        new_key = construct_redis_key("new-test-alias", "07.27")

        redis_con.lpush(old_key, "test-value")
        rename_redis_list("test-alias", "new-test-alias")

        self.assertFalse(redis_con.lrange(old_key, 0, -1))
        self.assertEqual(
            redis_con.lrange(new_key, 0, -1),
            ["test-value".encode("utf-8")],
        )

    @mock.patch("account.redis.from_url", FakeStrictRedis)
    def test_multiple_keys_renamed(self):
        redis_con = redis_connection()
        old_alias = "test-alias"
        new_alias = "new-test-alias"
        old_keys = [
            construct_redis_key(old_alias, "07.27"),
            construct_redis_key(old_alias, "07.26"),
            construct_redis_key(old_alias, "07.25"),
        ]
        new_keys = [
            construct_redis_key(new_alias, "07.27"),
            construct_redis_key(new_alias, "07.26"),
            construct_redis_key(new_alias, "07.25"),
        ]
        for old_key in old_keys:
            redis_con.lpush(old_key, "test-value")
        rename_redis_list(old_alias, new_alias)

        self.assertEqual(
            redis_con.scan(match=f"{old_alias}:*", count=60), (0, [])
        )

        new_keys_data = []
        for new_key in new_keys:
            new_keys_data.extend(redis_con.lrange(new_key, 0, -1))
        self.assertEqual(
            new_keys_data,
            [
                "test-value".encode("utf-8"),
                "test-value".encode("utf-8"),
                "test-value".encode("utf-8"),
            ],
        )

    @mock.patch("account.redis.from_url", FakeStrictRedis)
    def test_if_not_such_key_exists(self):
        redis_con = redis_connection()
        rename_redis_list("test-alias", "new-test-alias")

        self.assertFalse(redis_con.exists("new-test-alias"))
