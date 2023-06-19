from ast import alias
from django.test import TestCase
from account.models import Profile
from account.selectors import get_links_by_user

from shortener.models import Link


class GetLLinksByUserTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        cls.user_2 = Profile.objects.create_user(
            "test2@gmail.com", "test_password"
        )
        cls.links_data = (
            ("https://www.youtube.com/", "youtube"),
            ("https://www.linkedin.com/feed/", "linkedin"),
        )
        for link_data in cls.links_data:
            Link.objects.create(
                long_link=link_data[0],
                alias=link_data[1],
                user_profile=cls.user,
            )

    def test_return_empty_list(self):
        links = get_links_by_user(self.user_2)

        self.assertFalse(links)

    def test_returned_all_links(self):
        links = get_links_by_user(self.user)

        self.assertEqual(len(links), len(self.links_data))
