import datetime
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from shortener.models import Link
from shortener.services import update_link_statistics


class UpdateLinkStatisticsTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.link = Link.objects.create(
            long_link="https://google.com", alias="test-alias"
        )

    @mock.patch.object(
        timezone, "now", return_value=datetime.datetime(2023, 6, 15, 13, 20)
    )
    @mock.patch("shortener.services.append_to_redis_list", return_value=None)
    @mock.patch(
        "shortener.services.get_request_country_code", return_value="PL"
    )
    def test_method_execution(
        self, get_request_country_code_mock, append_to_redis_list_mock, _
    ):
        update_link_statistics("request", self.link)

        get_request_country_code_mock.assert_called_once_with("request")
        append_to_redis_list_mock.assert_called_once_with(
            self.link.alias, "PL"
        )
