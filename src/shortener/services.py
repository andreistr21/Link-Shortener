from ctypes import Union
import random
import string

from django.conf import settings
from django.forms import ModelForm

from .selectors import is_alias_free
import validators.url
from urllib.parse import urlparse


def save_link(shorten_form: ModelForm, alias=None) -> None:
    if alias:
        link = shorten_form.save(commit=False)
        link.alias = alias
        link.save()
    else:
        shorten_form.save()


def validate_str_for_allowed_values(str_to_validate: str) -> bool:
    allowed = settings.ALLOWED_CHARACTERS
    return all(character in allowed for character in str_to_validate)


def validate_str_for_restriction(str_to_validate: str) -> bool:
    restricted = settings.RESTRICTED_PHRASES
    return str_to_validate not in restricted


def alias_validation(alias: str, shorten_form=None) -> bool:
    """Checks alias for restricted characters and phrases, if alias if restricted, adds error to the form.
    Returns True if alias is can be used False otherwise"""
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


def short_with_alias(alias: str, shorten_form: ModelForm) -> None:
    """Saves shorten URL with alias or, if alias is taken, adds errors to the form"""
    if alias_validation(alias, shorten_form):
        if is_alias_free(alias):
            save_link(shorten_form, alias)
        else:
            shorten_form.add_error("alias", "This alias is unavailable")


def gen_random_str() -> str:
    letters = string.ascii_lowercase + string.digits

    return "".join(random.choice(letters) for _ in range(8))


def get_random_alias() -> str:
    """Returns random available alias"""
    alias = gen_random_str()
    while not alias_validation(alias) or not is_alias_free(alias):
        alias = gen_random_str()

    return alias


def short_with_random_value(shorten_form: ModelForm) -> str:
    alias = get_random_alias()
    save_link(shorten_form, alias)

    return alias


def validate_for_restricted_domains(link: str) -> bool:
    """Returns True if domain is allowed"""
    restricted_domains = settings.RESTRICTED_DOMAINS
    link_domain = urlparse(link).netloc
    # urlparse library can't find domain if there is no protocol extension
    if link_domain == "":
        link_domain = urlparse(f"https://{link}").netloc
    return False if link_domain == "" else link_domain not in restricted_domains


def link_validation(shorten_form: ModelForm) -> bool:
    link = shorten_form.cleaned_data.get("long_link")
    if validators.url(link) or validators.url(f"https://{link}"):
        if not validate_for_restricted_domains(link):
            shorten_form.add_error("long_link", "This domain is banned or invalid")
            return False
    else:
        shorten_form.add_error("long_link", "Enter a valid link")
        return False
    return True


def short_link(shorten_form: ModelForm) -> Union(None, str):
    alias = None
    if shorten_form.is_valid() and link_validation(shorten_form):
        if alias := shorten_form.cleaned_data.get("alias"):
            if len(alias) > 3:
                short_with_alias(alias, shorten_form)
            else:
                shorten_form.add_error("alias", "The alias must be at least 4 characters")
        else:
            alias = short_with_random_value(shorten_form)

    return alias
