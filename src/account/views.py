from django.shortcuts import redirect, render
from django.urls import reverse

from account.forms import SignUpForm
from account.services import send_activation_email

from .models import Profile
from .tokens import email_activation_token


def sign_up(request):
    sign_up_form = SignUpForm()
    if request.POST:
        sign_up_form = SignUpForm(request.POST)
        # TODO: Add additional email verification by validators module.
        if sign_up_form.is_valid():
            user = sign_up_form.save()
            send_activation_email(request, user, sign_up_form.cleaned_data.get("email"))
            return redirect(reverse("account:confirm_email"))

    return render(
        request,
        "account/sign_up.html",
        {
            "sign_up_form": sign_up_form,
        },
    )


def confirm_email(request):
    return render(request, "account/confirm_email.html")


def activate_email(request, pk, token):
    try:
        user = Profile.objects.get(pk=pk)
    except (TypeError, ValueError, OverflowError, Profile.DoesNotExist):
        user = None

    if user is not None and email_activation_token.check_token(user, token):
        user.is_email_confirmed = True
        user.save()

        return redirect(reverse("account:sing_up"))
    else:
        #TODO: Add an action if no such user is found.
        print("No such user")

    return redirect(reverse("shortener:index"))
