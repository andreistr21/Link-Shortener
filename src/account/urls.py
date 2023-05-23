from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import reverse_lazy
from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("sign-up/", views.sign_up, name="sign_up"),
    path("sign-in/", views.sign_in, name="sign_in"),
    path("confirm-email/", views.confirm_email, name="confirm_email"),
    path("new-confirmation-link/", views.new_confirmation_link, name="new_confirmation_link"),
    path("activate-email/<pk>/<token>", views.activate_email, name="activate_email"),
    path("overview", views.overview, name="overview"),
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="account/password_reset.html",
            email_template_name="account/email_password_reset_email.html",
            success_url=reverse_lazy("account:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="account/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="account/password_reset_confirm.html",
            success_url=reverse_lazy("account:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        PasswordResetCompleteView.as_view(template_name="account/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
