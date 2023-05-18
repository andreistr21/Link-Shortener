from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from shortener.forms import ShortenForm

from .services import short_link


def index(request: HttpRequest) -> HttpResponse:
    shorten_form = ShortenForm()
    shorten_link = None
    if request.POST:
        shorten_form = ShortenForm(request.POST)
        if shorten_form.is_valid():
            alias = short_link(shorten_form)
            # If form doesn't contain errors, that means that link was shortened and shorten link can be returned
            if shorten_form.is_valid():
                shorten_form = ShortenForm()
                shorten_link = f"{request.build_absolute_uri()}{alias}"

    return render(
        request,
        "shortener/shortener.html",
        {
            "shorten_form": shorten_form,
            "shorten_link": shorten_link,
        },
    )
