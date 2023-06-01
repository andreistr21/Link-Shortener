from django.test import TestCase

from account.models import Profile
from account.social_auth.pipeline.user import update_immutable_user_fields


class UpdateImmutableUserFieldsTests(TestCase):
    def setUp(self):
        self.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        self.user.save()

    def test_email_confirmation_status_update(self):
        resp = update_immutable_user_fields(self.user)
        user = resp["user"]
        db_user = Profile.objects.get(pk=user.pk)

        self.assertIsInstance(user, Profile)
        self.assertTrue(user.is_email_confirmed)
        self.assertEqual(user, db_user)
