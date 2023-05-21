from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("sign-up/", views.sign_up, name="sing_up"),
    path("confirm-email/", views.confirm_email, name="confirm_email"),
    path("activate-email/<pk>/<token>", views.activate_email, name="activate_email"),
]
