from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("sign-up/", views.sign_up, name="sing up"),
]
