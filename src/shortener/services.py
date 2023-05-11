import random
import string

from shortener.forms import ShortenForm

from .selectors import is_link_free


def save_link(shorten_form, shorten_link):
    link = shorten_form.save(commit=False)
    link.short_link = shorten_link
    link.save()


def short_with_alias(alias, shorten_form, absolute_uri):
    """Saves shorten URL with alias or, if alias is taken, adds error to the form"""
    if is_link_free(absolute_uri, alias):
        save_link(shorten_form, f"{absolute_uri}{alias}")
        return f"{absolute_uri}{alias}"

    shorten_form.add_error("alias", "This alias is unavailable")


def gen_random_str():
    letters = string.ascii_lowercase + string.digits

    return "".join(random.choice(letters) for _ in range(8))


def get_random_alias(absolute_uri):
    """Returns random available alias"""
    alias = gen_random_str()
    while not is_link_free(absolute_uri, alias):
        alias = gen_random_str()

    return f"{absolute_uri}{alias}"


def short_with_random_value(shorten_form, absolute_uri):
    shorten_link = get_random_alias(absolute_uri)
    save_link(shorten_form, shorten_link)

    return shorten_link


def short_link(request):
    shorten_form = ShortenForm(request.POST)
    if shorten_form.is_valid():
        absolute_uri = request.build_absolute_uri()
        if alias := shorten_form.cleaned_data.get("alias"):
            shorten_link = short_with_alias(alias, shorten_form, absolute_uri)
        else:
            shorten_link = short_with_random_value(shorten_form, absolute_uri)

    return shorten_form, shorten_link
