from django.test import RequestFactory, TestCase
from django.urls import reverse

from account.forms import ResetPasswordForm
from account.models import Profile


class ResetPasswordFormTests(TestCase):
    def setUp(self):
        Profile.objects.all().delete()
        self.factory = RequestFactory()
        profile = Profile.objects.create_user("test@gmail.com", "test_password")
        profile.is_email_confirmed = True
        profile.save()
        self.profile = Profile.objects.first()
        self.request = self.factory.get(reverse("account:sign_up"))
        self.request.user = self.profile

    def test_form_fields_have_placeholder_attributes(self):
        form = ResetPasswordForm(self.request)

        self.assertEqual(form.fields["new_password1"].widget.attrs["placeholder"], "New Password")
        self.assertEqual(
            form.fields["new_password2"].widget.attrs["placeholder"],
            "Repeat New Password",
        )

    def test_form_validation_with_valid_data(self):
        form_data = {
            "new_password1": "new_password",
            "new_password2": "new_password",
        }
        form = ResetPasswordForm(self.request, data=form_data)

        self.assertTrue(form.is_valid())

    def test_form_validation_with_mismatched_passwords(self):
        form_data = {
            "new_password1": "new_password",
            "new_password2": "different_password",
        }
        form = ResetPasswordForm(self.request, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.get("new_password2")[0], "The two password fields didn’t match."
        )
