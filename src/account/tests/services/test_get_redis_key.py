from unittest import mock
from django.test import TestCase

from account.services import get_redis_key


class GetRedisKeyTests(TestCase):
    @mock.patch("account.services.construct_redis_key")
    def test_returned_value(self, construct_redis_key_mock):
        date = "08.01"
        old_key = f"old-alias:{date}"
        new_alias = "new-alias"
        construct_redis_key_mock.return_value = f"{new_alias}:{date}"

        output = get_redis_key(old_key, new_alias)

        self.assertEqual(output, f"{new_alias}:{date}")
        construct_redis_key_mock.assert_called_once_with(new_alias, date)
