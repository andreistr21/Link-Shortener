from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.urls import reverse


class GetOrderByUserFriendlyTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.request_factory = RequestFactory()
        cls.template = Template(
            "{% load account_custom_tags %}{% get_order_by_user_friendly %}"
        )
        cls.user = get_user_model().objects.create(email="test@gmail.com")

    def test_order_returned(self):
        request = self.request_factory.get(
            reverse("account:links_list") + "?orderby=created_at"
        )

        rendered = self.template.render(Context({"request": request}))

        self.assertEqual(rendered, "Date - Oldest first")

    def test_if_no_such_order_by(self):
        request = self.request_factory.get(
            reverse("account:links_list") + "?orderby=do_not_exists"
        )

        rendered = self.template.render(Context({"request": request}))

        self.assertEqual(rendered, settings.LINK_DEFAULT_SORTING_STR)

    def test_if_no_order_by(self):
        request = self.request_factory.get(reverse("account:links_list"))

        rendered = self.template.render(Context({"request": request}))

        self.assertEqual(rendered, settings.LINK_DEFAULT_SORTING_STR)
