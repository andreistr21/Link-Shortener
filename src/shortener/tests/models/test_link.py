import random
import string
from datetime import datetime
from unittest import mock

from django.test import TestCase

from account.models import Profile
from shortener.forms import ShortenForm
from shortener.models import Link


class LinkTests(TestCase):
    def test_object_creation(self):
        mock_date = datetime(2023, 5, 17, 10, 16, 53, 599136)
        long_link = "https://www.youtube.com/"
        alias = "test-alias"
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = mock_date
            user = Profile.objects.create(email="user_username", password="user_password", last_online=mock_date)
            link = Link.objects.create(user_profile=user, long_link=long_link, alias=alias)

        self.assertEqual(link.user_profile, user)
        self.assertEqual(link.long_link, long_link)
        self.assertEqual(link.alias, alias)
        self.assertEqual(link.created_at, mock_date)

    def test_if_link_too_long(self):
        letters = string.ascii_lowercase + string.digits

        long_link = "https://www.youtube.com/" + "".join(random.choice(letters) for _ in range(2000))
        part_of_error_value = "Ensure this value has at most"
        shorten_form = ShortenForm(data={"long_link": long_link})
        shorten_form.is_valid()

        errors = shorten_form.errors.get("long_link")
        for error in errors:
            self.assertTrue(part_of_error_value in error)
