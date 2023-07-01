from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def get_order_by_user_friendly(context: dict) -> str:
    """Returns user friendly sorting name"""
    request = context.get("request")
    order_by = request.GET.get("orderby", "")
    sorting = settings.LINKS_SORTING_TYPES.copy()

    return sorting.get(order_by, settings.LINK_DEFAULT_SORTING_STR)
