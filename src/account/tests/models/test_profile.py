from django.test import TestCase
from account.models import Profile


class ProfileTest(TestCase):
    def test_user_creation(self):
        Profile.objects.create(email="test@gmail.com", password="test_password")
        profile = Profile.objects.first()
        self.assertTrue(profile)
        

