import random
import string

from django.conf import settings

from shortener.forms import ShortenForm

from .selectors import is_link_free
import validators.url
from urllib.parse import urlparse


def save_link(shorten_form, shorten_link):
    link = shorten_form.save(commit=False)
    link.short_link = shorten_link
    link.save()


def validate_str_for_allowed_values(str_to_validate: str, restricted_values: list) -> bool:
    return all(character in restricted_values for character in str_to_validate)


def validate_str_for_restriction(str_to_validate: str, restricted_values: list) -> bool:
    return str_to_validate not in restricted_values


def alias_validation(alias: str, shorten_form=None) -> bool:
    """Checks alias for restricted characters, if not, adds error to the form.
    Returns True if alias is free, False otherwise"""
    allowed = settings.ALLOWED_CHARACTERS
    restricted = settings.RESTRICTED_PHRASES
    if not validate_str_for_restriction(alias, restricted):
        if shorten_form:
            shorten_form.add_error("alias", "This alias is not allowed")
        return False
    if not validate_str_for_allowed_values(alias, allowed):
        if shorten_form:
            shorten_form.add_error("alias", "Only alphabetic characters and numerals are available for the alias")
        return False

    return True


def short_with_alias(alias, shorten_form, absolute_uri):
    """Saves shorten URL with alias or, if alias is taken, adds errors to the form"""
    if alias_validation(alias, shorten_form):
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
    while not alias_validation(alias) and not is_link_free(absolute_uri, alias):
        alias = gen_random_str()

    return f"{absolute_uri}{alias}"


def short_with_random_value(shorten_form, absolute_uri):
    shorten_link = get_random_alias(absolute_uri)
    save_link(shorten_form, shorten_link)

    return shorten_link


def validate_for_restricted_domains(link):
    restricted_domains = settings.RESTRICTED_DOMAINS
    link_domain = urlparse(link).netloc
    return link_domain not in restricted_domains


def link_validation(shorten_form):
    link = shorten_form.cleaned_data.get("long_link")
    if validators.url(link):
        if not validate_for_restricted_domains(link):
            shorten_form.add_error("long_link", "This domain is banned")
            return False
    else:
        shorten_form.add_error("long_link", "Enter a valid link")
        return False
    return True


def short_link(request):
    shorten_form = ShortenForm(request.POST)
    shorten_link = None
    if shorten_form.is_valid() and link_validation(shorten_form):
        absolute_uri = request.build_absolute_uri()
        if alias := shorten_form.cleaned_data.get("alias"):
            if len(alias) > 3:
                shorten_link = short_with_alias(alias, shorten_form, absolute_uri)
            else:
                shorten_form.add_error("alias", "The alias must be at least 4 characters")
        else:
            shorten_link = short_with_random_value(shorten_form, absolute_uri)

    return shorten_form, shorten_link
