from django.test import TestCase

from account.forms import SignUpForm
from account.services import get_username


class GetUsernameTests(TestCase):
    def setUp(self):
        self.form = SignUpForm(
            data={
                "email": "testEmail@gmail.com",
                "password1": "test_passPZ67",
                "password2": "test_passPZ67",
            }
        )
        self.form.is_valid()

    def test_email_extraction(self):
        username = get_username(self.form)

        self.assertEqual(username, "testEmail")
