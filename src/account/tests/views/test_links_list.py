from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from account.models import Profile
from account.views import links_list
from shortener.models import Link


class LinksListTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.request_factory = RequestFactory()
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
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
        # mock of  get_domain
        self.get_domain_patch = mock.patch("account.views.get_domain")
        self.get_domain_mock = self.get_domain_patch.start()
        self.addCleanup(self.get_domain_patch.stop)
        self.get_domain_mock.return_value = None

        # mock of  get_links_and_clicks
        self.get_links_and_clicks_patch = mock.patch(
            "account.views.get_links_and_clicks"
        )
        self.get_links_and_clicks_mock = (
            self.get_links_and_clicks_patch.start()
        )
        self.addCleanup(self.get_links_and_clicks_patch.stop)

    def test_redirect_bcs_of_anonymous_user(self):
        self.request = self.request_factory.get(reverse("account:links_list"))
        self.request.user = AnonymousUser()

        resp = links_list(self.request)
        resp.client = Client()

        self.assertEqual(resp.status_code, 302)

    def test_if_no_links_found(self):  # sourcery skip: class-extract-method
        self.request = self.request_factory.get(reverse("account:links_list"))
        self.request.user = self.user
        self.get_links_and_clicks_mock.return_value = []

        resp = links_list(self.request)

        self.assertIsInstance(resp, HttpResponse)
        self.assertEqual(resp.status_code, 200)
        self.get_domain_mock.assert_called_once()
        self.get_links_and_clicks_mock.assert_called_once_with(self.request)

    def test_if_links_found(self):
        self.request = self.request_factory.get(reverse("account:links_list"))
        self.request.user = self.user
        self.get_links_and_clicks_mock.return_value = self.mapped_clicks

        resp = links_list(self.request)

        self.assertIsInstance(resp, HttpResponse)
        self.assertEqual(resp.status_code, 200)
        self.get_domain_mock.assert_called_once()
        self.get_links_and_clicks_mock.assert_called_once_with(self.request)
