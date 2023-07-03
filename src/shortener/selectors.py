from django.shortcuts import get_object_or_404
from shortener.models import Link
from django.db.models import QuerySet


def is_alias_free(
    alias: str,
    exclude: None | Link = None,
) -> bool:
    link = Link.objects.filter(alias=alias)
    if exclude:
        link = link.exclude(pk=exclude.pk)
    return not link.exists()


def get_link(alias: str) -> QuerySet:
    """Retrieve link by alias or raises 404 error"""
    return get_object_or_404(Link, alias=alias)
