import datetime
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from account.models import Profile
from account.selectors import get_links_by_user
from shortener.models import Link


class GetLLinksByUserTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        cls.user_2 = Profile.objects.create_user(
            "test2@gmail.com", "test_password"
        )
        cls.links_data = (
            Link(
                long_link="https://www.youtube.com/",
                alias="youtube",
                user_profile=cls.user,
            ),
            Link(
                long_link="https://www.linkedin.com/feed/",
                alias="linkedin",
                user_profile=cls.user,
            ),
        )
        with mock.patch.object(
            timezone,
            "now",
            side_effect=[
                datetime.datetime(2023, 6, 19, 11, 40),
                datetime.datetime(2023, 6, 19, 12, 40),
            ],
        ):
            Link.objects.bulk_create(cls.links_data)

    def test_if_no_links(self):
        links = get_links_by_user(self.user_2)

        self.assertFalse(links)

    def test_if_no_links_with_filter(self):
        links = get_links_by_user(self.user_2, filter_by="linked")

        self.assertFalse(links)

    def test_if_no_links_with_order(self):
        links = get_links_by_user(self.user_2, order_by="created_at")

        self.assertFalse(links)

    def test_if_no_links_with_filter_and_order(self):
        links = get_links_by_user(
            self.user_2, filter_by="linked", order_by="created_at"
        )

        self.assertFalse(links)

    def test_if_links_exists(self):
        links = get_links_by_user(self.user)

        self.assertEqual(len(links), len(self.links_data))

    def test_if_links_exists_with_filter(self):
        links = get_links_by_user(self.user, filter_by="linked")

        self.assertEqual(list(links), [self.links_data[1]])

    def test_if_links_exists_with_order(self):
        links = get_links_by_user(self.user, order_by="created_at")

        self.assertEqual(list(links), list(self.links_data))

    def test_if_links_exists_with_filter_and_order(self):
        links = get_links_by_user(
            self.user, filter_by="e", order_by="created_at"
        )

        self.assertEqual(list(links), list(self.links_data))
