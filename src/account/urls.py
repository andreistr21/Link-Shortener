from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("sign-up/", views.sign_up, name="sing_up"),
    path("sign-in/", views.sign_in, name="sing_in"),
    path("confirm-email/", views.confirm_email, name="confirm_email"),
    path("new-confirmation-link/", views.new_confirmation_link, name="new_confirmation_link"),
    path("activate-email/<pk>/<token>", views.activate_email, name="activate_email"),
    path("overview", views.overview, name="overview"),
]
