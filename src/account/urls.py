from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from account import views
from account.decorators import anonymous_required
from account.forms import ResetPasswordEmailForm, ResetPasswordForm

app_name = "account"
urlpatterns = [
    path("sign-up/", views.sign_up, name="sign_up"),
    path("sign-in/", views.sign_in, name="sign_in"),
    path(
        "logout/",
        login_required(
            LogoutView.as_view(template_name="account/logged_out.html")
        ),
        name="logout",
    ),
    path("overview/", views.overview, name="overview"),
    path("links/", views.links_list, name="links_list"),
    path("links/<int:page>/", views.links_list, name="links_list"),
    # TODO: add tests
    path("link/<str:alias>/", views.link_statistics, name="link_statistics"),
    # TODO: add tests
    path("link/update/<str:alias>/", views.update_link, name="update_link"),
    path("confirm-email/", views.confirm_email, name="confirm_email"),
    path(
        "new-confirmation-link/",
        views.new_confirmation_link,
        name="new_confirmation_link",
    ),
    path(
        "activate-email/<uidb64>/<token>/",
        views.activate_email,
        name="activate_email",
    ),
    path(
        "password-reset/",
        anonymous_required(
            PasswordResetView.as_view(
                form_class=ResetPasswordEmailForm,
                template_name="account/password_reset.html",
                email_template_name="account/email_password_reset_email.html",
                success_url=reverse_lazy("account:password_reset_done"),
            )
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name="account/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        anonymous_required(
            PasswordResetConfirmView.as_view(
                form_class=ResetPasswordForm,
                template_name="account/password_reset_confirm.html",
                success_url=reverse_lazy("account:password_reset_complete"),
            )
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        PasswordResetCompleteView.as_view(
            template_name="account/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "privacy-policy/",
        TemplateView.as_view(template_name="account/privacy_policy.html"),
        name="privacy_policy",
    ),
    path(
        "terms-of-use/",
        TemplateView.as_view(template_name="account/terms_of_use.html"),
        name="terms_of_use",
    ),
]
