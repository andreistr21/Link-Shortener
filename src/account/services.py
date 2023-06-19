from profile import Profile

from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from account.selectors import (
    get_link_total_clicks,
    get_profile,
    get_profile_by_email,
)
from account.tasks import send_activation_email_task
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


# TODO: add tests
def get_domain() -> str:
    return settings.DEFAULT_DOMAIN


# TODO: add tests
def map_clicks_to_link(links: list[Link]) -> list[tuple[Link, str]]:
    """Returns list tuples with link and link clicks"""
    return [(link, get_link_total_clicks(link.alias)) for link in links]
