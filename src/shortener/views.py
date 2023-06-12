from cgi import print_arguments

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django_redis import get_redis_connection
from tzlocal import get_localzone

from shortener.forms import ShortenForm
from shortener.selectors import get_link
from shortener.services import short_link, update_link_statistics


def index(request: HttpRequest) -> HttpResponse:
    # cache.set("test-time", timezone.now())
    cache.set("test-time", {"time": timezone.now()})
    print(cache.get("test-time"))

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


def shorten_redirect(request: HttpRequest, url_alias: str) -> HttpResponse:
    link = get_link(url_alias)
    update_link_statistics(link)

    return redirect(link.long_link)
