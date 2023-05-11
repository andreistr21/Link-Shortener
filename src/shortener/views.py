from django.http import HttpResponse
from django.shortcuts import render

from shortener.forms import ShortenForm

from .services import short_link


def index(request) -> HttpResponse:
    shorten_form = ShortenForm()
    shorten_link = ""
    if request.POST:
        shorten_form, shorten_link = short_link(request)
        if shorten_form.is_valid():
            shorten_form = ShortenForm()

    return render(
        request,
        "shortener/shortener.html",
        {
            "shorten_form": shorten_form,
            "shorten_link": shorten_link,
        },
    )
