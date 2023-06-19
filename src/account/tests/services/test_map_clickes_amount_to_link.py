from unittest import mock

from django.test import TestCase

from account.services import map_clicks_amount_to_link
from shortener.models import Link


class MapClicksAmountToLinkTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.links = Link.objects.bulk_create(
            [
                Link(long_link="https://www.youtube.com/", alias="youtube1"),
                Link(long_link="https://www.youtube.com/", alias="youtube2"),
                Link(long_link="https://www.youtube.com/", alias="youtube3"),
            ]
        )

    @mock.patch("account.services.get_link_total_clicks", return_value=5)
    def test_one_link_in_list(self, _):
        mapped = map_clicks_amount_to_link([self.links[0]])

        self.assertEqual(len(mapped), 1)
        self.assertEqual(mapped, [(self.links[0], 5)])

    @mock.patch(
        "account.services.get_link_total_clicks", side_effect=[5, 8, 3]
    )
    def test_multiple_links_in_list(self, _):
        mapped = map_clicks_amount_to_link(self.links)

        self.assertEqual(len(mapped), 3)
        self.assertEqual(
            mapped,
            [(self.links[0], 5), (self.links[1], 8), (self.links[2], 3)],
        )
