from unittest import mock

from django.contrib.gis.geoip2 import GeoIP2
from django.test import TestCase
from geoip2.errors import AddressNotFoundError

from shortener.services import get_request_country_code


class GetRequestCountryCode(TestCase):
    @mock.patch("shortener.services.get_request_ip", return_value="127.0.0.1")
    @mock.patch.object(GeoIP2, "country_code", return_value="PL")
    def test_if_ip_in_db(self, *args):
        country_code = get_request_country_code("request")

        self.assertEqual(country_code, "PL")

    @mock.patch("shortener.services.get_request_ip", return_value="127.0.0.1")
    @mock.patch.object(
        GeoIP2,
        "country_code",
        return_value=None,
        side_effect=AddressNotFoundError(""),
    )
    def test_if_ip_not_in_db(self, *args):
        country_code = get_request_country_code("request")

        self.assertEqual(country_code, "")
