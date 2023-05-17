from django.test import TestCase

from shortener.forms import ShortenForm


class ShortenFormTests(TestCase):
    def test_long_link_field_attributes(self):
        shorten_form = ShortenForm()

        self.assertInHTML(
            '<input type="text" name="long_link" placeholder="Enter a long link to make a short one" autofocus="" maxlength="2000" required="" id="id_long_link">',
            str(shorten_form),
        )

    def test_alias_field_attributes(self):
        shorten_form = ShortenForm()

        self.assertInHTML(
            '<input type="text" name="alias" placeholder="Alias (Optional)" maxlength="80" id="id_alias">',
            str(shorten_form),
        )