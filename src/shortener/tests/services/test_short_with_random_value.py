from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from shortener.models import Link
from shortener.services import short_with_random_value
from shortener.forms import ShortenForm


class ShortWithRandomValueTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get(reverse("shortener:index"))
        self.request.user = AnonymousUser()
    
    def test_if_link_will_be_saved(self):
        long_link = "youtube.com"
        shorten_form = ShortenForm(data={"long_link": long_link})
        shorten_form.is_valid()
        short_with_random_value(self.request, shorten_form)
        
        self.assertTrue(Link.objects.filter(long_link=long_link).exists())
        
    def test_if_alias_returned(self):
        long_link = "youtube.com"
        shorten_form = ShortenForm(data={"long_link": long_link})
        shorten_form.is_valid()
        returned_alias = short_with_random_value(self.request, shorten_form)
        
        self.assertTrue(returned_alias)