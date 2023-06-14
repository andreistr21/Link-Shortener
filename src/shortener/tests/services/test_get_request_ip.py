from django.test import RequestFactory, TestCase
from django.urls import reverse

from shortener.services import get_request_ip


class GetRequestIpTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.request_factory = RequestFactory()

    def test_if_server_under_proxy(self):
        request = self.request_factory.get(
            reverse(
                "shortener:shorten_redirect", kwargs={"url_alias": "alias"}
            ),
            HTTP_X_FORWARDED_FOR="134.32.123.13",
        )
        ip = get_request_ip(request)

        self.assertEqual(ip, "134.32.123.13")

    def test_if_server_direct_con(self):  # sourcery skip: class-extract-method
        request = self.request_factory.get(
            reverse(
                "shortener:shorten_redirect", kwargs={"url_alias": "alias"}
            ),
            REMOTE_ADDR="134.32.124.13",
        )
        ip = get_request_ip(request)

        self.assertEqual(ip, "134.32.124.13")

    def test_if_server_has_no_ip(self):
        request = self.request_factory.get(
            reverse(
                "shortener:shorten_redirect", kwargs={"url_alias": "alias"}
            ),
            REMOTE_ADDR=None,
        )
        ip = get_request_ip(request)

        self.assertEqual(ip, "")
