from django.test import TestCase, override_settings

from account.services import get_domain


class GetDomainTests(TestCase):
    @override_settings(DEFAULT_DOMAIN="https://test-domain.com")
    def test_if_retrievable(self):
        domain = get_domain()
        
        self.assertEqual(domain, "https://test-domain.com")