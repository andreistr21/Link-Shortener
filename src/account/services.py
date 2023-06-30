import json
from datetime import datetime
from profile import Profile

from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from account.redis import redis_connection

from account.selectors import (
    get_link_statistics,
    get_link_total_clicks,
    get_links_by_user,
    get_profile,
    get_profile_by_email,
)
from account.tasks import send_activation_email_task
from account.temp import populate_redis_with_test_data
from account.tokens import email_activation_token
from shortener.models import Link


def update_email_confirmation_status(uidb64, token, status=True):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = get_profile(uid)

    if email_activation_token.check_token(user, token):
        user.is_email_confirmed = status
        user.save()


def _send_activation_email(request: HttpRequest, user, form):
    send_activation_email_task.delay(
        domain=get_current_site(request).domain,
        protocol=request.is_secure(),
        user_id=user.id,
        to_email=form.cleaned_data.get("email"),
    )


def get_username(sign_up_form: forms.Form) -> str:
    """Extracts first part of the email (up to "@" character)"""
    email = sign_up_form.cleaned_data["email"]

    return email.split("@")[0]


def save_new_user(sign_up_form: forms.Form) -> Profile:
    """Saves user and adds username"""
    user = sign_up_form.save()
    user.username = get_username(sign_up_form)
    user.save()
    return user


def sign_up_user(request, sign_up_form):
    if sign_up_form.is_valid():
        user = save_new_user(sign_up_form)
        _send_activation_email(request, user, sign_up_form)
        return redirect(reverse("account:confirm_email"))


def sign_in_user(request, sign_in_form):
    if sign_in_form.is_valid():
        login(request, sign_in_form.user_cache)
        return redirect(reverse("account:overview"))
    elif (
        len(sign_in_form.non_field_errors()) > 0
        and "Email for this account not confirmed."
        in sign_in_form.non_field_errors()[0]
    ):
        return "Error"


def send_new_activation_link(request, new_confirmation_link_form):
    """Sends a new activation link to user if email isn't confirmed"""
    if (
        not new_confirmation_link_form.is_valid()
        and new_confirmation_link_form.non_field_errors
        and "Email for this account not confirmed."
        in new_confirmation_link_form.non_field_errors()[0]
    ):
        user = get_profile_by_email(
            new_confirmation_link_form.cleaned_data.get("email")
        )
        _send_activation_email(request, user, new_confirmation_link_form)
        return redirect(reverse("account:confirm_email"))


def get_domain() -> str:
    return settings.DEFAULT_DOMAIN


def map_clicks_amount_to_link(links: list[Link]) -> list[tuple[Link, str]]:
    """Returns list tuples with link and link clicks"""
    return [(link, get_link_total_clicks(link.alias)) for link in links]


def sort_by_clicks(
    mapped_clicks: list[tuple[Link, str]], order_by: str
) -> list[tuple[Link, str]]:
    reverse = order_by == "-clicks"
    return sorted(mapped_clicks, key=lambda item: item[1], reverse=reverse)


def get_links_and_clicks(
    request: HttpRequest,
) -> list[tuple[Link, int]] | list:
    """Returns list of tuples with link and link clicks."""
    filter_by = request.GET.get("search")
    order_by = request.GET.get("orderby")
    order_by = (
        None
        if order_by not in settings.LINKS_SORTING_TYPES.keys()
        else order_by
    )
    clicks_sort = order_by in ["clicks", "-clicks"]

    if links := get_links_by_user(
        request.user, filter_by, None if clicks_sort else order_by
    ):
        mapped_clicks = map_clicks_amount_to_link(links)
        if clicks_sort:
            mapped_clicks = sort_by_clicks(mapped_clicks, order_by)
        return mapped_clicks
    return []


# TODO:Add tests
def get_charts_data(
    link_statistics: list[tuple[str, str]]
) -> tuple[dict[str, int], dict[str, int]]:
    clicks_chart_data = {}
    countries_chart_data = {}

    for stat in link_statistics:
        parsed_stat = json.loads(stat)
        date = datetime.fromisoformat(parsed_stat["time"]).strftime("%m.%d")
        if not clicks_chart_data.get(date):
            clicks_chart_data[date] = 0
        clicks_chart_data[date] += 1

        country_code = parsed_stat["country"]
        if not countries_chart_data.get(country_code):
            countries_chart_data[country_code] = 0
        countries_chart_data[country_code] += 1

    return clicks_chart_data, countries_chart_data


# TODO:Add tests
def get_link_datasets(link: Link):
    link_statistics = get_link_statistics(link.alias)
    clicks_chart_data, countries_chart_data = get_charts_data(link_statistics)
    if countries_chart_data.get(""):
        countries_chart_data["Unknown"] = countries_chart_data.pop("")

    clicks_chart_dataset = json.dumps(
        {
            "title": "Clicks in last 60 days",
            "data": {
                "labels": list(clicks_chart_data.keys()),
                "datasets": [
                    {
                        "label": "Clicks",
                        "backgroundColor": "#20a7f8",
                        "data": list(clicks_chart_data.values()),
                    }
                ],
            },
        }
    )
    country_chart_dataset = json.dumps(
        {
            "title": "Clicks by Country",
            "data": {
                "labels": list(countries_chart_data.keys()),
                "datasets": [
                    {
                        "label": "Clicks",
                        "data": list(countries_chart_data.values()),
                    }
                ],
            },
        }
    )

    return clicks_chart_dataset, country_chart_dataset


# TODO: add tests
def check_user_access(user: Profile, link: Link) -> None | Http404:
    """Raises 404 if link don't belongs to the user."""
    if link not in user.links.all():
        raise Http404()


# TODO: add tests
def rename_redis_list(old_alias: str, new_alias: str):
    redis_connection().rename(old_alias, new_alias)
