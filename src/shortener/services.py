import random
import string

from django.conf import settings

from shortener.forms import ShortenForm

from .selectors import is_alias_free
import validators.url
from urllib.parse import urlparse


def save_link(shorten_form, alias):
    link = shorten_form.save(commit=False)
    link.alias = alias
    link.save()


def validate_str_for_allowed_values(str_to_validate: str) -> bool:
    allowed = settings.ALLOWED_CHARACTERS
    return all(character in allowed for character in str_to_validate)


def validate_str_for_restriction(str_to_validate: str) -> bool:
    restricted = settings.RESTRICTED_PHRASES
    return str_to_validate not in restricted


def alias_validation(alias: str, shorten_form=None) -> bool:
    """Checks alias for restricted characters, if not, adds error to the form.
    Returns True if alias is free, False otherwise"""
    if not validate_str_for_restriction(alias):
        if shorten_form:
            shorten_form.add_error("alias", "This alias is not allowed")
        return False
    if not validate_str_for_allowed_values(alias):
        if shorten_form:
            shorten_form.add_error(
                "alias", "Only alphabetic characters, numerals and hyphen are available for the alias"
            )
        return False

    return True


def short_with_alias(alias, shorten_form):
    """Saves shorten URL with alias or, if alias is taken, adds errors to the form"""
    if alias_validation(alias, shorten_form):
        if is_alias_free(alias):
            save_link(shorten_form, alias)
        else:
            shorten_form.add_error("alias", "This alias is unavailable")


def gen_random_str():
    letters = string.ascii_lowercase + string.digits

    return "".join(random.choice(letters) for _ in range(8))


def get_random_alias():
    """Returns random available alias"""
    alias = gen_random_str()
    while not alias_validation(alias) and not is_alias_free(alias):
        alias = gen_random_str()

    return alias


def short_with_random_value(shorten_form):
    alias = get_random_alias()
    save_link(shorten_form, alias)


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
    if shorten_form.is_valid() and link_validation(shorten_form):
        absolute_uri = request.build_absolute_uri()
        if alias := shorten_form.cleaned_data.get("alias"):
            if len(alias) > 3:
                short_with_alias(alias, shorten_form)
            else:
                shorten_form.add_error("alias", "The alias must be at least 4 characters")
        else:
            short_with_random_value(shorten_form)

    return shorten_form, absolute_uri + alias
