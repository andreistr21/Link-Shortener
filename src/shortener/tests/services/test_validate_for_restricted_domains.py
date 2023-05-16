from unittest import TestCase

from shortener.services import validate_for_restricted_domains


class ValidateForRestrictedDomainsTests(TestCase):
    def test_with_restricted_domains(self):
        restricted_links = [
            "http://127.0.0.1:8000",
            "https://127.0.0.1:8000",
            "http://127.0.0.1:8000/",
            "https://127.0.0.1:8000/",
            "http://127.0.0.1:8000/some-link",
            "https://127.0.0.1:8000/link-test",
        ]

        for link in restricted_links:
            self.assertFalse(validate_for_restricted_domains(link))

    def test_with_allowed_domains(self):
        allowed_links = [
            "https://www.youtube.com/",
            "https://www.dropbox.com/login?cont=%2Fhome",
            "https://languagetool.org/",
            "https://www.freeopenvpn.org/index.php",
            "https://www.binance.com/en/blog/ecosystem/binance-api-spot-trading-with-postman-2584865726555369951",
            "https://www.vpnjantit.com/free-openvpn",
            "https://iplogger.org/",
        ]

        for link in allowed_links:
            self.assertTrue(validate_for_restricted_domains(link))
