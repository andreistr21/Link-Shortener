from django.test import TestCase

from shortener.services import get_random_alias
from shortener.models import Link


class GetRandomAliasTests(TestCase):
    def _is_alias_free(self, alias):
        return not Link.objects.filter(alias=alias).exists()

    def test_if_given_alias_free(self):
        for _ in range(100):
            alias = get_random_alias()
            self.assertTrue(self._is_alias_free(alias))
