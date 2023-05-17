from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from shortener.forms import ShortenForm


class IndexTests(TestCase):
    def test_call_with_get(self):
        response = self.client.get(reverse("shortener:index"))
        empty_shortener_form = ShortenForm()
        empty_shortener_form.is_valid()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shortener/shortener.html")
        self.assertFalse(bool(response.context.get("shorten_form").data.get("long_link")))
        self.assertEqual(response.context.get("shorten_link"), None)

    def test_if_form_is_invalid(self):
        response = self.client.post(reverse("shortener:index"), {"long_link": ""})

        self.assertTrue(bool(response.context.get("shorten_form").errors))
        self.assertEqual(response.context.get("shorten_link"), None)

    def test_if_form_is_valid(self):
        response = self.client.post(reverse("shortener:index"), {"long_link": "https://www.youtube.com"})

        self.assertTrue(bool(response.context.get("shorten_link")))
        
        