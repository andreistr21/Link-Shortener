from django.http import Http404
from django.test import TestCase

from account.models import Profile
from account.services import check_user_access
from shortener.models import Link


class CheckUserAccess(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.users = Profile.objects.bulk_create(
            [
                Profile(email="test@gmail.com", password="test-password"),
                Profile(email="test2@gmail.com", password="test-password"),
            ]
        )
        cls.links = Link.objects.bulk_create(
            [
                Link(
                    long_link="https://www.youtube.com/",
                    alias="youtube1",
                    user_profile=cls.users[0],
                ),
                Link(
                    long_link="https://www.youtube.com/",
                    alias="youtube2",
                    user_profile=cls.users[0],
                ),
                Link(
                    long_link="https://www.youtube.com/",
                    alias="youtube3",
                ),
            ]
        )

    def test_exception_raise(self):
        self.assertRaises(
            Http404,
            check_user_access,
            self.users[1],
            self.links[2],
        )

    def test_if_user_has_access(self):
        resp = check_user_access(self.users[0], self.links[0])
        
        self.assertIsNone(resp)
