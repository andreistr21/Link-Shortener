from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from account.selectors import get_profile
from account.tokens import email_activation_token


def construct_email(domain, protocol, user_id, to_email):
    user = get_profile(user_id)
    mail_subject = "Activate your user account."
    message = render_to_string(
        "account/email_activation.html",
        {
            "user": user.email,
            "domain": domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": email_activation_token.make_token(user),
            "protocol": "https" if protocol else "http",
        },
    )

    return EmailMessage(mail_subject, message, to=[to_email])


@shared_task
def send_activation_email_task(domain, protocol, user_id, to_email):
    construct_email(domain, protocol, user_id, to_email).send()
