from unittest import mock

from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from account.models import Profile
from account.views import overview
from shortener.models import Link


class TestOverviewTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        cls.request_factory = RequestFactory()
        cls.links = Link.objects.bulk_create(
            [
                Link(long_link="https://www.youtube.com/", alias="youtube1"),
                Link(long_link="https://www.youtube.com/", alias="youtube2"),
                Link(long_link="https://www.youtube.com/", alias="youtube3"),
            ]
        )

    def setUp(self) -> None:
        self.request = self.request_factory.get(reverse("account:overview"))
        self.request.user = self.user

    @mock.patch(
        "account.views.get_domain", return_value="http://127.0.0.1:8000"
    )
    @mock.patch("account.views.map_clicks_amount_to_link", return_value=[])
    @mock.patch("account.views.get_links_total_clicks", return_value=[])
    @mock.patch("account.views.get_links_by_user", return_value=[])
    def test_no_links(
        self,
        get_links_by_user_mock,
        get_links_total_clicks_mock,
        map_clicks_amount_to_link_mock,
        get_domain_mock,
    ):
        response = overview(self.request)

        self.assertIsInstance(response, HttpResponse)
        get_links_by_user_mock.assert_called_once_with(self.request.user)
        get_links_total_clicks_mock.assert_not_called()
        map_clicks_amount_to_link_mock.assert_not_called()
        get_domain_mock.assert_called_once()

    @mock.patch(
        "account.views.get_domain", return_value="http://127.0.0.1:8000"
    )
    @mock.patch("account.views.map_clicks_amount_to_link")
    @mock.patch("account.views.get_links_total_clicks")
    @mock.patch("account.views.get_links_by_user")
    def test_with_multiple_links(
        self,
        get_links_by_user_mock,
        get_links_total_clicks_mock,
        map_clicks_amount_to_link_mock,
        get_domain_mock,
    ):
        get_links_by_user_mock.return_value = self.links
        get_links_total_clicks_mock.return_value = 20
        map_clicks_amount_to_link_mock.return_value = [
            (self.links[0], 7),
            (self.links[1], 4),
            (self.links[2], 9),
        ]

        response = overview(self.request)

        self.assertIsInstance(response, HttpResponse)
        get_links_by_user_mock.assert_called_once_with(self.request.user)
        get_links_total_clicks_mock.assert_called_once_with(self.links)
        map_clicks_amount_to_link_mock.assert_called_once_with(self.links[:3])
        get_domain_mock.assert_called_once()
