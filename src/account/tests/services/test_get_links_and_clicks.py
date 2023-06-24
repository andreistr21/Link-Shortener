from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from account.services import get_links_and_clicks
from shortener.models import Link


class GetLinksAndClicksTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.request_factory = RequestFactory()
        cls.links = Link.objects.bulk_create(
            [
                Link(
                    long_link="https://www.youtube.com/",
                    alias="youtube1",
                ),
                Link(
                    long_link="https://www.youtube.com/",
                    alias="youtube2",
                ),
                Link(
                    long_link="https://www.linkedin.com/feed/",
                    alias="linkedin",
                ),
            ]
        )
        cls.mapped_clicks = [
            (cls.links[0], 9),
            (cls.links[1], 3),
            (cls.links[2], 5),
        ]

    def setUp(self) -> None:
        # mock of  get_links_by_user
        self.get_links_by_user_patch = mock.patch(
            "account.services.get_links_by_user"
        )
        self.get_links_by_user_mock = self.get_links_by_user_patch.start()

        self.addCleanup(self.get_links_by_user_patch.stop)

        # mock of map_clicks_amount_to_link
        self.map_clicks_amount_to_link_patch = mock.patch(
            "account.services.map_clicks_amount_to_link"
        )
        self.map_clicks_amount_to_link_mock = (
            self.map_clicks_amount_to_link_patch.start()
        )

        self.addCleanup(self.map_clicks_amount_to_link_patch.stop)

        # mock of sort_by_clicks
        self.sort_by_clicks_patch = mock.patch(
            "account.services.sort_by_clicks"
        )
        self.sort_by_clicks_mock = self.sort_by_clicks_patch.start()

        self.addCleanup(self.sort_by_clicks_patch.stop)

    def test_if_no_links_found(self):
        self.request = self.request_factory.get(reverse("account:links_list"))
        self.request.user = AnonymousUser()
        self.get_links_by_user_mock.return_value = []

        resp = get_links_and_clicks(self.request)

        self.assertFalse(resp)
        self.get_links_by_user_mock.assert_called_once_with(
            self.request.user, None, None
        )
        self.map_clicks_amount_to_link_mock.assert_not_called()
        self.sort_by_clicks_mock.assert_not_called()

    def test_links_returned(self):  # sourcery skip: class-extract-method
        self.request = self.request_factory.get(reverse("account:links_list"))
        self.request.user = AnonymousUser()
        self.get_links_by_user_mock.return_value = self.links
        self.map_clicks_amount_to_link_mock.return_value = self.mapped_clicks

        resp = get_links_and_clicks(self.request)

        self.assertEqual(resp, self.mapped_clicks)
        self.get_links_by_user_mock.assert_called_once_with(
            self.request.user, None, None
        )
        self.map_clicks_amount_to_link_mock.assert_called_once_with(self.links)
        self.sort_by_clicks_mock.assert_not_called()

    def test_links_returned_with_filter(self):
        # sourcery skip: class-extract-method
        self.request = self.request_factory.get(
            reverse("account:links_list") + "?search=youtube"
        )
        self.request.user = AnonymousUser()
        self.get_links_by_user_mock.return_value = self.links[:2]
        self.map_clicks_amount_to_link_mock.return_value = self.mapped_clicks[
            :2
        ]

        resp = get_links_and_clicks(self.request)

        self.assertEqual(resp, self.mapped_clicks[:2])
        self.get_links_by_user_mock.assert_called_once_with(
            self.request.user, "youtube", None
        )
        self.map_clicks_amount_to_link_mock.assert_called_once_with(
            self.links[:2]
        )
        self.sort_by_clicks_mock.assert_not_called()

    def test_links_returned_with_order_by_date(self):
        self.request = self.request_factory.get(
            reverse("account:links_list") + "?orderby=created_at"
        )
        self.request.user = AnonymousUser()
        self.get_links_by_user_mock.return_value = self.links[::-1]
        self.map_clicks_amount_to_link_mock.return_value = self.mapped_clicks[
            ::-1
        ]

        resp = get_links_and_clicks(self.request)

        self.assertEqual(resp, self.mapped_clicks[::-1])
        self.get_links_by_user_mock.assert_called_once_with(
            self.request.user, None, "created_at"
        )
        self.map_clicks_amount_to_link_mock.assert_called_once_with(
            self.links[::-1]
        )
        self.sort_by_clicks_mock.assert_not_called()

    def test_links_returned_with_order_by_clicks(self):
        # sourcery skip: class-extract-method
        self.request = self.request_factory.get(
            reverse("account:links_list") + "?orderby=-clicks"
        )
        self.request.user = AnonymousUser()
        sorted_mapped_clicks = [
            self.mapped_clicks[0],
            self.mapped_clicks[2],
            self.mapped_clicks[1],
        ]
        self.get_links_by_user_mock.return_value = self.links
        self.map_clicks_amount_to_link_mock.return_value = self.mapped_clicks
        self.sort_by_clicks_mock.return_value = sorted_mapped_clicks

        resp = get_links_and_clicks(self.request)

        self.assertEqual(resp, sorted_mapped_clicks)
        self.get_links_by_user_mock.assert_called_once_with(
            self.request.user, None, None
        )
        self.map_clicks_amount_to_link_mock.assert_called_once_with(self.links)
        self.sort_by_clicks_mock.assert_called_once_with(
            self.mapped_clicks, "-clicks"
        )

    def test_links_returned_with_wrong_order_by(self):
        self.request = self.request_factory.get(
            reverse("account:links_list") + "?orderby=test"
        )
        self.request.user = AnonymousUser()
        self.get_links_by_user_mock.return_value = self.links
        self.map_clicks_amount_to_link_mock.return_value = self.mapped_clicks

        resp = get_links_and_clicks(self.request)

        self.assertEqual(resp, self.mapped_clicks)
        self.get_links_by_user_mock.assert_called_once_with(
            self.request.user, None, None
        )
        self.map_clicks_amount_to_link_mock.assert_called_once_with(self.links)
        self.sort_by_clicks_mock.assert_not_called()

    def test_links_returned_with_filter_and_order_by_date(self):
        self.request = self.request_factory.get(
            reverse("account:links_list")
            + "?search=youtube&orderby=created_at"
        )
        self.request.user = AnonymousUser()
        self.get_links_by_user_mock.return_value = self.links[:2][::-1]
        self.map_clicks_amount_to_link_mock.return_value = self.mapped_clicks[
            :2
        ][::-1]

        resp = get_links_and_clicks(self.request)

        self.assertEqual(resp, self.mapped_clicks[:2][::-1])
        self.get_links_by_user_mock.assert_called_once_with(
            self.request.user, "youtube", "created_at"
        )
        self.map_clicks_amount_to_link_mock.assert_called_once_with(
            self.links[:2][::-1]
        )
        self.sort_by_clicks_mock.assert_not_called()

    def test_links_returned_with_filter_and_wrong_order_by(self):
        self.request = self.request_factory.get(
            reverse("account:links_list") + "?search=youtube&orderby=test"
        )
        self.request.user = AnonymousUser()
        self.get_links_by_user_mock.return_value = self.links[:2]
        self.map_clicks_amount_to_link_mock.return_value = self.mapped_clicks[
            :2
        ]

        resp = get_links_and_clicks(self.request)

        self.assertEqual(resp, self.mapped_clicks[:2])
        self.get_links_by_user_mock.assert_called_once_with(
            self.request.user, "youtube", None
        )
        self.map_clicks_amount_to_link_mock.assert_called_once_with(
            self.links[:2]
        )
        self.sort_by_clicks_mock.assert_not_called()
