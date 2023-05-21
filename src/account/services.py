from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .tokens import email_activation_token


def construct_email(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string(
        "account/email_activation.html",
        {
            "user": user.email,
            "domain": get_current_site(request).domain,
            "pk": user.pk,
            # "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": email_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )

    return EmailMessage(mail_subject, message, to=[to_email])


def send_activation_email(request, user, to_email):
    construct_email(request, user, to_email).send()
