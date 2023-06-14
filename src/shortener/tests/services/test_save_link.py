from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from account.models import Profile
from shortener.forms import ShortenForm
from shortener.models import Link
from shortener.services import save_link


class SaveLinkTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )

    def setUp(self) -> None:
        Link.objects.all().delete()
        self.client = Client()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get(reverse("shortener:index"))

    def test_save_with_form_and_alias_anonymous_user(self):
        # sourcery skip: class-extract-method
        self.request.user = AnonymousUser()

        long_link = "youtube.com"
        alias = "test-short-link"
        shorten_form = ShortenForm(data={"long_link": long_link})
        save_link(self.request, shorten_form, alias)

        link = Link.objects.get(long_link=long_link)
        self.assertTrue(link)
        self.assertFalse(link.user_profile)

    def test_save_with_form_and_alias_auth_user(self):
        self.request.user = self.user

        long_link = "youtube.com"
        alias = "test-short-link"
        shorten_form = ShortenForm(data={"long_link": long_link})
        save_link(self.request, shorten_form, alias)

        link = Link.objects.get(long_link=long_link)
        self.assertTrue(link)
        self.assertEqual(link.user_profile, self.user)

    def test_save_with_form_only_anonymous_user(self):
        self.request.user = AnonymousUser()

        long_link = "youtube.com"
        shorten_form = ShortenForm(data={"long_link": long_link})
        save_link(self.request, shorten_form)

        link = Link.objects.get(long_link=long_link)
        self.assertTrue(link)
        self.assertFalse(link.user_profile)

    def test_save_with_form_only_auth_user(self):
        self.request.user = self.user

        long_link = "youtube.com"
        shorten_form = ShortenForm(data={"long_link": long_link})
        save_link(self.request, shorten_form)

        link = Link.objects.get(long_link=long_link)
        self.assertTrue(link)
        self.assertEqual(link.user_profile, self.user)

    def test_save_with_existing_long_link_anonymous_user(self):
        # sourcery skip: class-extract-method
        self.request.user = AnonymousUser()

        long_link = "youtube.com"
        shorten_form_1 = ShortenForm(data={"long_link": long_link})
        shorten_form_2 = ShortenForm(data={"long_link": long_link})
        save_link(self.request, shorten_form_1)
        save_link(self.request, shorten_form_2)

        links = Link.objects.filter(long_link=long_link)
        self.assertTrue(len(links) == 2)
        self.assertFalse(links[0].user_profile)
        self.assertFalse(links[1].user_profile)

    def test_save_with_existing_long_link_auth_user(self):
        self.request.user = self.user

        long_link = "youtube.com"
        shorten_form_1 = ShortenForm(data={"long_link": long_link})
        shorten_form_2 = ShortenForm(data={"long_link": long_link})
        save_link(self.request, shorten_form_1)
        save_link(self.request, shorten_form_2)

        links = Link.objects.filter(long_link=long_link)
        self.assertTrue(len(links) == 2)
        self.assertEqual(links[0].user_profile, self.user)
        self.assertEqual(links[1].user_profile, self.user)
