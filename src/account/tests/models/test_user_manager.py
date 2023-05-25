from django.test import TestCase
from account.models import Profile


class UserManagerTests(TestCase):
    def setUp(self):
        Profile.objects.all().delete()

    def test__create_user_method(self):
        Profile.objects._create_user(email="test@gmail.com", password="test_password")
        self.assertTrue(Profile.objects.first())

    def test__create_user_method_without_email(self):
        self.assertRaises(
            ValueError, Profile.objects._create_user, email="", password="test_password"
        )

    def test_create_user_method(self):
        Profile.objects.create_user(email="test@gmail.com", password="test_password")
        self.assertTrue(Profile.objects.first())

    def test_create_user_method_staff_user(self):
        Profile.objects.create_user(
            email="test@gmail.com", password="test_password", is_staff=True
        )
        profile = Profile.objects.first()

        self.assertTrue(profile.is_staff)

    def test_create_user_method_superuser(self):
        # sourcery skip: class-extract-method
        Profile.objects.create_user(
            email="test@gmail.com", password="test_password", is_staff=True, is_superuser=True
        )
        profile = Profile.objects.first()

        self.assertTrue(profile.is_staff)
        self.assertTrue(profile.is_superuser)

    def test_create_user_method_superuser_not_staff(self):
        Profile.objects.create_user(
            email="test@gmail.com", password="test_password", is_superuser=True
        )
        profile = Profile.objects.first()

        self.assertFalse(profile.is_staff)
        self.assertTrue(profile.is_superuser)

    def test_create_superuser_method_explicitly(self):
        Profile.objects.create_superuser(
            email="test@gmail.com", password="test_password", is_staff=True, is_superuser=True
        )
        profile = Profile.objects.first()

        self.assertTrue(profile.is_staff)
        self.assertTrue(profile.is_superuser)

    def test_create_superuser_method_implicitly(self):
        Profile.objects.create_superuser(email="test@gmail.com", password="test_password")
        profile = Profile.objects.first()

        self.assertTrue(profile.is_staff)
        self.assertTrue(profile.is_superuser)

    def test_create_superuser_method_not_stuff(self):
        self.assertRaises(
            ValueError,
            Profile.objects.create_superuser,
            email="test@gmail.com",
            password="test_password",
            is_staff=False,
        )

    def test_create_superuser_method_not_superuser(self):
        self.assertRaises(
            ValueError,
            Profile.objects.create_superuser,
            email="test@gmail.com",
            password="test_password",
            is_superuser=False,
        )
