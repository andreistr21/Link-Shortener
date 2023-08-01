from django.test import TestCase

from account.services import construct_redis_key


class ConstructRedisKeyTests(TestCase):
    def test_returned_data(self):
        alias = "test-alias"
        date = "08.01"

        output = construct_redis_key(alias, date)

        self.assertEqual(output, f"{alias}:{date}")
