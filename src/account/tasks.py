from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from celery import shared_task

from .models import Profile

from .tokens import email_activation_token


# def construct_email(request, user, to_email):
#     mail_subject = "Activate your user account."
#     message = render_to_string(
#         "account/email_activation.html",
#         {
#             "user": user.email,
#             "domain": get_current_site(request).domain,
#             "pk": user.pk,
#             # "uid": urlsafe_base64_encode(force_bytes(user.pk)),
#             "token": email_activation_token.make_token(user),
#             "protocol": "https" if request.is_secure() else "http",
#         },
#     )

#     return EmailMessage(mail_subject, message, to=[to_email])


@shared_task
def send_activation_email(domain, protocol, user_id, to_email):
    user = get_object_or_404(Profile, pk=user_id)
    mail_subject = "Activate your user account."
    message = render_to_string(
        "account/email_activation.html",
        {
            "user": user.email,
            "domain": domain,
            "pk": user.pk,
            # "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": email_activation_token.make_token(user),
            "protocol": "https" if protocol else "http",
        },
    )

    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
    
    # construct_email(request, user, to_email).send()
