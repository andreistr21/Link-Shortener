from django.urls import path

from . import views

app_name = "shortener"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:url_alias>/", views.shorten_redirect, name="shorten_redirect"),
]
