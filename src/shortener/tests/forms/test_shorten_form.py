from django.test import TestCase

from shortener.forms import ShortenForm
from shortener.services import save_link


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

    def test_if_alias_exists(self):
        long_link = "youtube.com"
        alias = "test-short-link"
        shorten_form_1 = ShortenForm(data={"long_link": long_link, "alias": alias})
        save_link(shorten_form_1)
        shorten_form_2 = ShortenForm(data={"long_link": long_link, "alias": alias})
        shorten_form_2.is_valid()
        error = shorten_form_2.errors
        expected_errors_value = {"alias": ["Link with this Alias already exists."]}

        self.assertEqual(error, expected_errors_value)
