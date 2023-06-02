from django.contrib.auth.forms import PasswordResetForm
from django.test import TestCase

from account.forms import ResetPasswordEmailForm


class ResetPasswordEmailFormTests(TestCase):
    def test_form_instantiation(self):
        form = ResetPasswordEmailForm()
        self.assertIsInstance(form, PasswordResetForm)

    def test_email_field_placeholder(self):
        form = ResetPasswordEmailForm()

        email_field = form.fields["email"]
        self.assertTrue(
            email_field.widget.attrs.get("placeholder") == "Your email"
        )
