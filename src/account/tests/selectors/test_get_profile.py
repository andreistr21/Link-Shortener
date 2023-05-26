from django.http import Http404
from django.test import TestCase

from account.models import Profile
from account.selectors import get_profile


class GetProfileTests(TestCase):
    def test_get_profile_valid_pk(self):
        profile_created = Profile.objects.create_user("emal@gmail.com", "test_password")

        self.assertTrue(get_profile(pk=profile_created.pk))

    def test_get_profile_invalid_pk(self):
        Profile.objects.create_user("emal@gmail.com", "test_password")

        self.assertRaises(Http404, get_profile, pk=3)
