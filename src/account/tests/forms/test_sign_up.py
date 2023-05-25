import email
from django.test import TestCase

from account.forms import SignUpForm


class SignUpFormTests(TestCase):
    def test_email_field_html(self):
        self.assertInHTML(
            (
                '<input type="email" name="email" placeholder="Your email" maxlength="150"'
                ' autofocus="" required="" id="id_email">'
            ),
            str(SignUpForm()),
        )

    def test_password1_field_html(self):
        self.assertInHTML(
            (
                '<input type="password" name="password1" autocomplete="new-password"'
                ' placeholder="Password" required="" id="id_password1">'
            ),
            str(SignUpForm()),
        )

    def test_password2_field_html(self):
        self.assertInHTML(
            (
                '<input type="password" name="password2" autocomplete="new-password"'
                ' placeholder="Repeat password" required="" id="id_password2">'
            ),
            str(SignUpForm()),
        )
