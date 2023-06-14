from django.shortcuts import get_object_or_404
from shortener.models import Link


def is_alias_free(alias: str) -> bool:
    return not Link.objects.filter(alias=alias).exists()


def get_link(alias: str) -> Link:
    """Retrieve link by alias or raises 404 error"""
    return get_object_or_404(Link, alias=alias)
