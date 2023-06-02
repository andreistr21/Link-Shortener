from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from account.decorators import anonymous_required
from account.forms import SignInForm, SignUpForm
from account.services import (
    send_new_activation_link,
    sign_in_user,
    sign_up_user,
    update_email_confirmation_status,
)


@anonymous_required
def sign_up(request):
    sign_up_form = SignUpForm()
    if request.POST:
        sign_up_form = SignUpForm(request.POST)
        if http_response_redirect := sign_up_user(request, sign_up_form):
            return http_response_redirect

    return render(
        request,
        "account/sign_up.html",
        {
            "sign_up_form": sign_up_form,
        },
    )


@anonymous_required
def sign_in(request):
    new_activation_link = False
    sign_in_form = SignInForm()
    if request.POST:
        sign_in_form = SignInForm(request, request.POST)
        resp = sign_in_user(request, sign_in_form)
        if type(resp) is HttpResponseRedirect:
            return resp
        elif resp == "Error":
            new_activation_link = True

    return render(
        request,
        "account/sign_in.html",
        {
            "sign_in_form": sign_in_form,
            "new_activation_link": new_activation_link,
        },
    )


def confirm_email(request):
    return render(request, "account/confirm_email.html")


@anonymous_required
def activate_email(_, pk, token):
    update_email_confirmation_status(pk, token)

    return redirect(reverse("account:sign_in"))


@login_required
def overview(request: HttpRequest) -> HttpResponse:
    return render(request, "account/overview.html", {})


@anonymous_required
def new_confirmation_link(request: HttpRequest) -> HttpResponse:
    """Sending new confirmation link to email"""
    new_confirmation_link_form = SignInForm()
    if request.POST:
        new_confirmation_link_form = SignInForm(request, request.POST)
        if http_resp_redirect := send_new_activation_link(
            request, new_confirmation_link_form
        ):
            return http_resp_redirect

    return render(
        request,
        "account/new_confirmation_link.html",
        {
            "new_confirmation_link_form": new_confirmation_link_form,
        },
    )
