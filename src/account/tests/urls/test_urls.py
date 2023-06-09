from unittest import mock

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.paginator import Paginator
from django.http import QueryDict
from django.test import Client, TestCase
from django.urls import resolve, reverse
from django.views.generic import TemplateView

from account import views
from account.models import Profile
from shortener.forms import ShortenForm
from shortener.models import Link


class AccountUrlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_email = "test@gmail.com"
        cls.user_password = "test_password"
        cls.user = Profile.objects.create_user(
            cls.user_email, cls.user_password
        )
        cls.anonymous_require_redirect_name = "account:overview"
        cls.login_required_redirect_name = "account:sign_in"
        cls.link = Link.objects.create(
            long_link="https://www.youtube.com", alias="youtube"
        )

    def setUp(self):
        self.client = Client()
        self.client.user = AnonymousUser()

    def _test_template_used(self, response, template_name):
        self.assertTemplateUsed(response, template_name)

    def _test_url_status(self, response, status_code=200):
        self.assertEqual(response.status_code, status_code)

    def _test_redirect(self, response, redirect_url):
        self.assertRedirects(response, redirect_url)

    def _test_view_used(self, response, expected_view):
        view_name = resolve(response.request["PATH_INFO"]).func.__name__
        if view_name == "view":
            view_name = expected_view.__name__
        expected_view_name = expected_view.__name__

        self.assertEqual(view_name, expected_view_name)

    def _login(self):
        self.client.force_login(self.user)

    def _test_view_render(self, response, view, template_name=None):
        self._test_url_status(response)
        self._test_view_used(response, view)
        if template_name:
            self._test_template_used(response, template_name)

    def _test_view_redirect(
        self, response, view, redirect_name=None, next=None, redirect_args=None
    ):
        if not redirect_name:
            redirect_name = self.anonymous_require_redirect_name

        if next:
            expected_url = f"{reverse(redirect_name)}{next}"
            self._test_redirect(response, expected_url)
        elif redirect_args:
            self._test_redirect(
                response, reverse(redirect_name, args=redirect_args)
            )
        else:
            self._test_redirect(response, reverse(redirect_name))

        self._test_view_used(response, view)

    def _get_mapped_clicks_list(self):
        class testLink:
            alias = "link_obj"

        return [
            (testLink(), 9),
            (testLink(), 3),
            (testLink(), 5),
            (testLink(), 6),
            (testLink(), 2),
            (testLink(), 10),
            (testLink(), 54),
            (testLink(), 1),
            (testLink(), 9),
            (testLink(), 3),
            (testLink(), 5),
            (testLink(), 6),
            (testLink(), 2),
            (testLink(), 10),
            (testLink(), 54),
            (testLink(), 1),
            (testLink(), 9),
            (testLink(), 3),
            (testLink(), 5),
            (testLink(), 6),
            (testLink(), 2),
            (testLink(), 10),
            (testLink(), 54),
            (testLink(), 1),
            (testLink(), 9),
            (testLink(), 3),
            (testLink(), 5),
            (testLink(), 6),
            (testLink(), 2),
            (testLink(), 10),
            (testLink(), 54),
            (testLink(), 1),
            (testLink(), 9),
            (testLink(), 3),
            (testLink(), 5),
            (testLink(), 6),
            (testLink(), 2),
            (testLink(), 10),
            (testLink(), 54),
            (testLink(), 1),
            (testLink(), 9),
            (testLink(), 3),
            (testLink(), 5),
            (testLink(), 6),
            (testLink(), 2),
            (testLink(), 10),
            (testLink(), 54),
            (testLink(), 1),
        ]

    def test_sign_up_url_anonymous_user(self):
        response = self.client.get(reverse("account:sign_up"))

        self._test_view_render(response, views.sign_up)

    def test_sign_up_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:sign_up"))

        self._test_view_redirect(response, views.sign_up)

    def test_sign_in_url_anonymous_user(self):
        response = self.client.get(reverse("account:sign_in"))

        self._test_view_render(response, views.sign_in)

    def test_sign_in_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:sign_in"))

        self._test_view_redirect(response, views.sign_in)

    def test_logout_url_anonymous_user(self):
        response = self.client.get(reverse("account:logout"))

        self._test_view_redirect(
            response,
            LogoutView,
            self.login_required_redirect_name,
            "?next=/account/logout/",
        )

    def test_logout_url_auth_user(self):  # sourcery skip: class-extract-method
        self._login()
        response = self.client.get(reverse("account:logout"))

        self._test_view_render(
            response,
            LogoutView,
            "account/logged_out.html",
        )

    def test_overview_url_anonymous_user(self):
        response = self.client.get(reverse("account:overview"))

        self._test_view_redirect(
            response,
            views.overview,
            self.login_required_redirect_name,
            "?next=/account/overview/",
        )

    def test_overview_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:overview"))

        self._test_view_render(response, views.overview)
        self.assertEqual(response.context["total_clicks"], 0)
        self.assertEqual(response.context["mapped_links"], [])
        self.assertEqual(response.context["view_more"], False)
        self.assertEqual(response.context["domain"], "http://127.0.0.1:8000")

    @mock.patch("account.views.get_domain", return_value="https://shorty.com")
    @mock.patch("account.views.get_links_and_clicks", return_value="")
    def test_links_url_with_default_page_anonymous_user(
        self, get_links_and_clicks_mock, _
    ):
        response = self.client.get(reverse("account:links_list"))

        self.assertRedirects(
            response, reverse("account:sign_in") + "?next=/account/links/"
        )

    @mock.patch("account.views.get_domain", return_value="https://shorty.com")
    @mock.patch("account.views.get_links_and_clicks")
    def test_links_url_with_default_page_auth_user(
        self, get_links_and_clicks_mock, _
    ):
        mapped_clicks = self._get_mapped_clicks_list()
        get_links_and_clicks_mock.return_value = mapped_clicks
        paginator = Paginator(mapped_clicks, settings.LINKS_ITEMS_PER_PAGE)
        page_obj = paginator.get_page(1)

        self._login()
        response = self.client.get(reverse("account:links_list"))

        self._test_view_render(
            response, views.links_list, "account/links_list.html"
        )
        self.assertEqual(response.context["domain"], "https://shorty.com")
        self.assertEqual(
            response.context["page_obj"].object_list,
            page_obj.object_list,
        )
        self.assertEqual(response.context["current_query_str"], "")
        self.assertEqual(response.context["current_query_dict"], {})

    @mock.patch("account.views.get_domain", return_value="https://shorty.com")
    @mock.patch("account.views.get_links_and_clicks", return_value="")
    def test_links_url_with_retrieved_page_anonymous_user(
        self, get_links_and_clicks_mock, _
    ):
        response = self.client.get(reverse("account:links_list", args=(2,)))

        self.assertRedirects(
            response, reverse("account:sign_in") + "?next=/account/links/2/"
        )

    @mock.patch("account.views.get_domain", return_value="https://shorty.com")
    @mock.patch("account.views.get_links_and_clicks")
    def test_links_url_with_retrieved_page_auth_user(
        self, get_links_and_clicks_mock, _
    ):
        mapped_clicks = self._get_mapped_clicks_list()
        get_links_and_clicks_mock.return_value = mapped_clicks
        paginator = Paginator(mapped_clicks, settings.LINKS_ITEMS_PER_PAGE)
        page_obj = paginator.get_page(2)

        self._login()
        response = self.client.get(reverse("account:links_list", args=(2,)))

        self._test_view_render(
            response, views.links_list, "account/links_list.html"
        )
        self.assertEqual(response.context["domain"], "https://shorty.com")
        self.assertEqual(
            response.context["page_obj"].object_list,
            page_obj.object_list,
        )
        self.assertEqual(response.context["current_query_str"], "")
        self.assertEqual(response.context["current_query_dict"], {})

    @mock.patch("account.views.get_domain", return_value="https://shorty.com")
    @mock.patch("account.views.get_links_and_clicks")
    def test_links_url_with_retrieved_page_with_query_auth_user(
        self, get_links_and_clicks_mock, _
    ):
        mapped_clicks = self._get_mapped_clicks_list()
        get_links_and_clicks_mock.return_value = mapped_clicks
        paginator = Paginator(mapped_clicks, settings.LINKS_ITEMS_PER_PAGE)
        page_obj = paginator.get_page(2)

        self._login()
        response = self.client.get(
            reverse("account:links_list", args=(2,))
            + "?search=wiki&orderby=date"
        )

        self._test_view_render(
            response, views.links_list, "account/links_list.html"
        )
        self.assertEqual(response.context["domain"], "https://shorty.com")
        self.assertEqual(
            response.context["page_obj"].object_list,
            page_obj.object_list,
        )
        self.assertEqual(
            response.context["current_query_str"], "search=wiki&orderby=date"
        )
        self.assertEqual(
            response.context["current_query_dict"],
            QueryDict("search=wiki&orderby=date"),
        )

    def test_link_url_anonymous_user(self):
        response = self.client.get(
            reverse("account:link_statistics", args=(self.link.alias,))
        )

        self.assertRedirects(
            response,
            reverse("account:sign_in")
            + "?next="
            + reverse("account:link_statistics", args=(self.link.alias,)),
        )

    @mock.patch("account.views.get_link_total_clicks", return_value=10)
    @mock.patch("account.views.get_domain", return_value="https://shorty.com")
    @mock.patch("account.views.check_user_access", return_value=None)
    @mock.patch("account.views.get_link_datasets")
    @mock.patch("account.views.get_link")
    def test_link_url_auth_user(
        self, get_link_mock, get_link_datasets_mock, *args
    ):
        get_link_mock.return_value = self.link
        get_link_datasets_mock.return_value = (
            "clicks_chart_dataset",
            "country_chart_dataset",
        )
        self._login()

        response = self.client.get(
            reverse("account:link_statistics", args=(self.link.alias,))
        )

        self._test_view_render(
            response, views.link_statistics, "account/link_statistics.html"
        )
        self.assertEqual(response.context["link"], self.link)
        self.assertEqual(response.context["domain"], "https://shorty.com")
        self.assertEqual(
            response.context["clicks_chart_dataset"], "clicks_chart_dataset"
        )
        self.assertEqual(
            response.context["country_chart_dataset"], "country_chart_dataset"
        )
        self.assertEqual(response.context["link_clicks"], 10)

    def test_link_update_url_anonymous_user(self):
        response = self.client.get(
            reverse("account:update_link", args=(self.link.alias,))
        )

        self.assertRedirects(
            response,
            reverse("account:sign_in")
            + "?next="
            + reverse("account:update_link", args=(self.link.alias,)),
        )

    @mock.patch("account.views.check_user_access", return_value=None)
    @mock.patch("account.views.get_link")
    def test_link_update_url_auth_user_get(self, get_link_mock, *args):
        get_link_mock.return_value = self.link
        self._login()

        response = self.client.get(
            reverse("account:update_link", args=(self.link.alias,))
        )

        self._test_view_render(
            response, views.update_link, "account/update_link.html"
        )
        self.assertIsInstance(
            response.context["update_link_form"], ShortenForm
        )

    @mock.patch("account.views.get_link_datasets", return_value=(None, None))
    @mock.patch("account.views.short_link", return_value="youtube")
    @mock.patch.object(ShortenForm, "is_valid", return_value=True)
    @mock.patch("account.views.check_user_access", return_value=None)
    @mock.patch("account.views.get_link")
    def test_link_update_url_auth_user_post(
        self, get_link_mock, short_link_mock, *args
    ):
        get_link_mock.return_value = self.link
        self._login()
        form_data = {
            "long_link": "https://www.youtube.com/",
            "alias": "youtube",
        }

        response = self.client.post(
            reverse("account:update_link", args=(self.link.alias,)),
            data=form_data,
        )

        self._test_view_redirect(
            response,
            views.update_link,
            "account:link_statistics",
            redirect_args=(self.link.alias,),
        )

    def test_link_delete_url_anonymous_user(self):
        response = self.client.get(
            reverse("account:delete_link", args=(self.link.alias,))
        )

        self._test_view_redirect(
            response,
            views.delete_link,
            "account:sign_in",
            next=(
                f'?next={reverse("account:delete_link", args=(self.link.alias,))}'
            ),
        )

    @mock.patch("account.views.remove_link")
    @mock.patch("account.views.check_user_access")
    @mock.patch("account.views.get_link")
    def test_link_delete_url_auth_user(self, get_link_mock, *args):
        get_link_mock.return_value = self.link
        self._login()

        response = self.client.get(
            reverse("account:delete_link", args=(self.link.alias,))
        )

        self._test_view_redirect(
            response, views.delete_link, "account:links_list"
        )

    def test_confirm_email_url_anonymous_user(self):
        response = self.client.get(reverse("account:confirm_email"))

        self._test_view_render(response, views.confirm_email)

    def test_confirm_email_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:confirm_email"))

        self._test_view_render(response, views.confirm_email)

    def test_new_confirmation_link_url_anonymous_user(self):
        response = self.client.get(reverse("account:new_confirmation_link"))

        self._test_view_render(response, views.new_confirmation_link)

    def test_new_confirmation_link_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:new_confirmation_link"))

        self._test_view_redirect(response, views.new_confirmation_link)

    @mock.patch(
        "account.views.update_email_confirmation_status",
        return_value=None,
    )
    def test_activate_email_url_anonymous_user(self, _):
        response = self.client.get(
            reverse("account:activate_email", args=("pk", "token"))
        )

        self._test_view_redirect(
            response, views.activate_email, "account:sign_in"
        )

    def test_activate_email_url_auth_user(self):
        self._login()
        response = self.client.get(
            reverse("account:activate_email", args=("pk", "token"))
        )

        self._test_view_redirect(response, views.activate_email)

    def test_password_reset_url_anonymous_user(self):
        response = self.client.get(reverse("account:password_reset"))

        self._test_view_render(
            response, PasswordResetView, "account/password_reset.html"
        )

    def test_password_reset_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:password_reset"))

        self._test_view_redirect(response, PasswordResetView)

    def test_password_reset_done_url_anonymous_user(self):
        response = self.client.get(reverse("account:password_reset_done"))

        self._test_view_render(
            response, PasswordResetDoneView, "account/password_reset_done.html"
        )

    def test_password_reset_done_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:password_reset_done"))

        self._test_view_render(
            response, PasswordResetDoneView, "account/password_reset_done.html"
        )

    def test_password_reset_confirm_url_anonymous_user(self):
        response = self.client.get(
            reverse("account:password_reset_confirm", args=["uidb64", "token"])
        )

        self._test_view_render(
            response,
            PasswordResetConfirmView,
            "account/password_reset_confirm.html",
        )

    def test_password_reset_confirm_url_auth_user(self):
        self._login()
        response = self.client.get(
            reverse("account:password_reset_confirm", args=("uidb64", "token"))
        )

        self._test_view_redirect(response, PasswordResetConfirmView)

    def test_password_reset_complete_url_anonymous_user(self):
        response = self.client.get(reverse("account:password_reset_complete"))

        self._test_view_render(
            response,
            PasswordResetCompleteView,
            "account/password_reset_complete.html",
        )

    def test_password_reset_complete_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:password_reset_complete"))

        self._test_view_render(
            response,
            PasswordResetCompleteView,
            "account/password_reset_complete.html",
        )

    def test_privacy_policy_url_anonymous_user(self):
        response = self.client.get(reverse("account:privacy_policy"))

        self._test_view_render(
            response, TemplateView, "account/privacy_policy.html"
        )

    def test_privacy_policy_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:privacy_policy"))

        self._test_view_render(
            response, TemplateView, "account/privacy_policy.html"
        )

    def test_terms_of_use_url_anonymous_user(self):
        response = self.client.get(reverse("account:terms_of_use"))

        self._test_view_render(
            response, TemplateView, "account/terms_of_use.html"
        )

    def test_terms_of_use_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:terms_of_use"))

        self._test_view_render(
            response, TemplateView, "account/terms_of_use.html"
        )
