from django.shortcuts import render

from account.forms import SignUpForm


def sign_up(request):
    sign_up_form = SignUpForm()
    if request.POST:
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            sign_up_form.save()
            sign_up_form = SignUpForm()

    return render(
        request,
        "account/sign_up.html",
        {
            "sign_up_form": sign_up_form,
        },
    )
