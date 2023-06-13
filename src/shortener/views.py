from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from shortener.forms import ShortenForm
from shortener.selectors import get_link
from shortener.services import short_link, update_link_statistics


def index(request: HttpRequest) -> HttpResponse:
    shorten_form = ShortenForm()
    shorten_link = None
    if request.POST:
        shorten_form = ShortenForm(request.POST)
        if shorten_form.is_valid():
            alias = short_link(request, shorten_form)
            # If form doesn't contain errors, that means that link
            # was shortened and shorten link can be returned
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


# TODO: add tests
def shorten_redirect(request: HttpRequest, url_alias: str) -> HttpResponse:
    link = get_link(url_alias)
    update_link_statistics(request, link)

    return redirect(link.long_link)
