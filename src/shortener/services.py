import json
import random
import string
from typing import Optional
from urllib.parse import urlparse

import validators.url
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils import timezone
from geoip2.errors import AddressNotFoundError

from shortener.forms import ShortenForm
from shortener.models import Link
from shortener.redis import redis_connection
from shortener.selectors import is_alias_free

g = GeoIP2()


def save_link(
    request: HttpRequest, shorten_form: ModelForm, alias=None
) -> None:
    link = shorten_form.save(commit=False)

    if alias:
        link.alias = alias
    if request.user.is_authenticated:
        link.user_profile = request.user

    link.save()


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
                "alias",
                (
                    "Only alphabetic characters, numerals and hyphen are"
                    " available for the alias"
                ),
            )
        return False

    return True


def short_with_alias(
    request: HttpRequest,
    alias: str,
    shorten_form: ModelForm,
    exclude: None | Link = None,
) -> None:
    """Saves shorten URL with alias or, if alias is taken, adds errors to the form"""
    if alias_validation(alias, shorten_form):
        if is_alias_free(alias, exclude):
            save_link(request, shorten_form, alias)
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


def short_with_random_value(
    request: HttpRequest, shorten_form: ModelForm
) -> str:
    alias = get_random_alias()
    save_link(request, shorten_form, alias)

    return alias


def validate_for_restricted_domains(link: str) -> bool:
    """Returns True if domain is allowed"""
    restricted_domains = settings.RESTRICTED_DOMAINS
    link_domain = urlparse(link).netloc
    return (
        False if link_domain == "" else link_domain not in restricted_domains
    )


def link_validation(shorten_form: ModelForm) -> bool:
    link = shorten_form.cleaned_data.get("long_link")
    if validators.url(link): # type: ignore
        if not validate_for_restricted_domains(link):
            shorten_form.add_error(
                "long_link", "This domain is banned or invalid"
            )
            return False
    else:
        shorten_form.add_error("long_link", "Enter a valid link")
        return False
    return True


def short_link(
    request: HttpRequest, shorten_form: ShortenForm, exclude=None
) -> Optional[str]:
    alias = None
    if shorten_form.is_valid() and link_validation(shorten_form):
        if alias := shorten_form.cleaned_data.get("alias"):
            if len(alias) > 3:
                short_with_alias(request, alias, shorten_form, exclude)
            else:
                shorten_form.add_error(
                    "alias", "The alias must be at least 4 characters"
                )
        else:
            alias = short_with_random_value(request, shorten_form)

    return alias


def get_request_ip(request: HttpRequest) -> str:
    """Retrieves ip from request and returns it or empty string."""
    if forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"):
        return forwarded_for.split(",")[0].strip()
    if remote_addr := request.META.get("REMOTE_ADDR"):
        return remote_addr.split(",")[0].strip()
    return ""


def get_request_country_code(request: HttpRequest) -> str:
    """Returns code of the country from which request is made from"""
    ip = get_request_ip(request)
    try:
        country_code = g.country_code(ip)
    except AddressNotFoundError:
        country_code = ""
    return country_code


def append_to_redis_list(alias: str, country_code: str) -> None:
    list_key = f"{alias}:{timezone.now().strftime('%m.%d')}"
    redis_con = redis_connection()
    exists = redis_con.exists(list_key)

    redis_con.lpush(
        list_key,
        json.dumps(
            {"time": timezone.now().isoformat(), "country": country_code}
        ),
    )

    if not exists:
        redis_con.expire(list_key, settings.REDIS_TTL)


def update_link_statistics(request: HttpRequest, link: Link) -> None:
    country_code = get_request_country_code(request)
    append_to_redis_list(link.alias, country_code)
