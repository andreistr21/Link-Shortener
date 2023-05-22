from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from account.forms import SignInForm, SignUpForm
from account.tasks import send_activation_email

from .models import Profile
from .tokens import email_activation_token


def sign_up(request):
    sign_up_form = SignUpForm()
    if request.POST:
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            user = sign_up_form.save()
            send_activation_email.delay(
                domain=get_current_site(request).domain,
                protocol=request.is_secure(),
                user_id=user.id,
                to_email=sign_up_form.cleaned_data.get("email"),
            )
            return redirect(reverse("account:confirm_email"))

    return render(
        request,
        "account/sign_up.html",
        {
            "sign_up_form": sign_up_form,
        },
    )


def sign_in(request):
    new_activation_link = False
    sign_in_form = SignInForm()
    if request.POST:
        sign_in_form = SignInForm(request, request.POST)
        if sign_in_form.is_valid():
            login(request, sign_in_form.user_cache)
            return redirect(reverse("account:overview"))
        elif "Email for this account not confirmed." in sign_in_form.non_field_errors()[0]:
            new_activation_link = True
            print(f"{new_activation_link=}")

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


def activate_email(_, pk, token):
    try:
        user = Profile.objects.get(pk=pk)
    except (TypeError, ValueError, OverflowError, Profile.DoesNotExist):
        user = None

    if user is not None and email_activation_token.check_token(user, token):
        user.is_email_confirmed = True
        user.save()

        return redirect(reverse("account:sing_up"))
    else:
        # TODO: Add an action if no such user is found.
        print("No such user")

    return redirect(reverse("shortener:index"))


def overview(request: HttpRequest) -> HttpResponse:
    return render(request, "account/overview.html", {})


def new_confirmation_link(request: HttpRequest) -> HttpResponse:
    new_confirmation_link_form = SignInForm()
    if request.POST:
        new_confirmation_link_form = SignInForm(request, request.POST)
        if (
            not new_confirmation_link_form.is_valid()
            and new_confirmation_link_form.non_field_errors
            and "Email for this account not confirmed." in new_confirmation_link_form.non_field_errors()[0]
        ):
            user = get_object_or_404(Profile, email=new_confirmation_link_form.cleaned_data.get("email"))
            send_activation_email.delay(
                domain=get_current_site(request).domain,
                protocol=request.is_secure(),
                user_id=user.id,
                to_email=new_confirmation_link_form.cleaned_data.get("email"),
            )
            return redirect(reverse("account:confirm_email"))

    return render(
        request,
        "account/new_confirmation_link.html",
        {
            "new_confirmation_link_form": new_confirmation_link_form,
        },
    )
