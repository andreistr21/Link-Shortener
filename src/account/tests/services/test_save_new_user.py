from unittest import mock
from django.test import TestCase

from account.forms import SignUpForm
from account.models import Profile
from account.services import save_new_user


class SaveNewUserTests(TestCase):
    def setUp(self):
        self.form = SignUpForm(
            data={
                "email": "testEmail@gmail.com",
                "password1": "test_passPZ67",
                "password2": "test_passPZ67",
            }
        )
        self.form.is_valid()
        
    @mock.patch("account.services.get_username", return_value="test_username")
    def test_user_creation(self, _):
        user = save_new_user(self.form)
        db_user = Profile.objects.get(pk=user.pk)
        
        self.assertEqual(db_user.username, "test_username")
