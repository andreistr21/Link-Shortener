from django.http import Http404
from django.test import TestCase

from account.models import Profile
from account.selectors import get_profile_by_email


class GetProfileByEmailTests(TestCase):
    def test_get_profile_valid_email(self):
        profile_created = Profile.objects.create_user("emal@gmail.com", "test_password")

        self.assertTrue(get_profile_by_email(email=profile_created.email))

    def test_get_profile_invalid_email(self):
        Profile.objects.create_user("emal@gmail.com", "test_password")

        self.assertRaises(Http404, get_profile_by_email, email="invalid@gmail.com")
