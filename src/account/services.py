from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

from account.selectors import get_profile, get_profile_by_email
from account.tasks import send_activation_email_task
from account.tokens import email_activation_token


def update_email_confirmation_status(pk, token, status=True):
    user = get_profile(pk)

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


def sign_up_user(request, sign_up_form):
    if sign_up_form.is_valid():
        user = sign_up_form.save()
        _send_activation_email(request, user, sign_up_form)
        return redirect(reverse("account:confirm_email"))


def sign_in_user(request, sign_in_form):
    if sign_in_form.is_valid():
        login(request, sign_in_form.user_cache)
        return redirect(reverse("account:overview"))
    elif (
        "Email for this account not confirmed."
        in sign_in_form.non_field_errors()[0]
    ):
        return "Error"


def send_new_activation_link(request, new_confirmation_link_form):
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
