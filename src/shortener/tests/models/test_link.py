from datetime import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase

from account.models import Profile
from shortener.models import Link


class LinkTests(TestCase):
    def test_object_creation(self):
        mock_date = datetime(2023, 5, 17, 10, 16, 53, 599136)
        long_link = "https://www.youtube.com/"
        alias = "test-alias"
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = mock_date
            user = User.objects.create(username="user_username", password="user_password")
            user_profile = Profile.objects.create(user=user, last_online=mock_date)
            link = Link.objects.create(user_profile=user_profile, long_link=long_link, alias=alias)

        self.assertEqual(link.user_profile, user_profile)
        self.assertEqual(link.long_link, long_link)
        self.assertEqual(link.alias, alias)
        self.assertEqual(link.created_at, mock_date)
