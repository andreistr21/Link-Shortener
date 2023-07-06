import json
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from account.models import Profile
from account.views import link_statistics
from shortener.models import Link


class LinkStatisticsTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.request_factory = RequestFactory()
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        cls.link = Link.objects.create(
            long_link="https://www.youtube.com/", alias="youtube1"
        )
        cls.clicks_chart_data = {"30.06": 3, "29.06": 2}
        cls.expected_countries_chart_data = {
            "PL": 2,
            "DE": 1,
            "ES": 2,
            "Unknown": 1,
        }
        cls.expected_clicks_chart_dataset = json.dumps(
            {
                "title": "Clicks in last 60 days",
                "data": {
                    "labels": list(cls.clicks_chart_data.keys()),
                    "datasets": [
                        {
                            "label": "Clicks",
                            "backgroundColor": "#20a7f8",
                            "data": list(cls.clicks_chart_data.values()),
                        }
                    ],
                },
            }
        )
        cls.expected_country_chart_dataset = json.dumps(
            {
                "title": "Clicks by Country",
                "data": {
                    "labels": list(cls.expected_countries_chart_data.keys()),
                    "datasets": [
                        {
                            "label": "Clicks",
                            "data": list(
                                cls.expected_countries_chart_data.values()
                            ),
                        }
                    ],
                },
            }
        )

    def setUp(self) -> None:
        # mocking get_domain
        self.get_domain_patch = mock.patch("account.views.get_domain")
        self.get_domain_mock = self.get_domain_patch.start()
        self.addCleanup(self.get_domain_patch.stop)
        self.get_domain_mock.return_value = None

    def test_login_required_redirect(self):
        request = self.request_factory.get(
            reverse("account:link_statistics", args=(self.link.alias,))
        )
        request.user = AnonymousUser()

        response = link_statistics(request, self.link.alias)
        response.client = Client()

        self.assertRedirects(
            response,
            reverse("account:sign_in")
            + "?next="
            + reverse("account:link_statistics", args=(self.link.alias,)),
        )

    @mock.patch("account.views.get_link_total_clicks", return_value=10)
    @mock.patch("account.views.check_user_access", return_value=None)
    @mock.patch("account.views.get_link_datasets")
    @mock.patch("account.views.get_link")
    def test_auth_user(
        self, get_link_mock, get_link_datasets_mock, check_user_access_mock, get_link_total_clicks_mock
    ):
        get_link_mock.return_value = self.link
        get_link_datasets_mock.return_value = (
            self.expected_country_chart_dataset,
            self.expected_country_chart_dataset,
        )
        request = self.request_factory.get(
            reverse("account:link_statistics", args=(self.link.alias,))
        )
        request.user = self.user

        response = link_statistics(request, self.link.alias)
        response.client = Client()

        self.assertEqual(response.status_code, 200)
        get_link_mock.assert_called_once_with(self.link.alias)
        get_link_datasets_mock.assert_called_once_with(self.link)
        check_user_access_mock.assert_called_once_with(request.user, self.link)
        get_link_total_clicks_mock.assert_called_once_with(self.link.alias)

    @mock.patch("account.views.get_link_datasets")
    @mock.patch("account.views.get_link")
    def test_auth_user_no_link_found(
        self, get_link_mock, get_link_datasets_mock
    ):
        get_link_mock.return_value = None
        get_link_mock.side_effect = Http404
        get_link_datasets_mock.return_value = (
            self.expected_country_chart_dataset,
            self.expected_country_chart_dataset,
        )
        request = self.request_factory.get(
            reverse("account:link_statistics", args=(self.link.alias,))
        )
        request.user = self.user

        self.assertRaises(Http404, link_statistics, request, self.link.alias)

    @mock.patch("account.views.check_user_access", return_value=None)
    @mock.patch("account.views.get_link_datasets")
    @mock.patch("account.views.get_link")
    def test_auth_user_link_do_not_belongs_to_current_user(
        self, get_link_mock, get_link_datasets_mock, check_user_access_mock
    ):
        get_link_mock.return_value = self.link
        get_link_datasets_mock.return_value = (
            self.expected_country_chart_dataset,
            self.expected_country_chart_dataset,
        )
        check_user_access_mock.return_value = None
        check_user_access_mock.side_effect = Http404
        request = self.request_factory.get(
            reverse("account:link_statistics", args=(self.link.alias,))
        )
        request.user = self.user

        self.assertRaises(Http404, link_statistics, request, self.link.alias)
