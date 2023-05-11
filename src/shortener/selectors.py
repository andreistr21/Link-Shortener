from .models import Link


def is_link_free(absolute_uri, alias):
    restricted_aliases = ["", "admin", alias]
    restricted_urls = [f"{absolute_uri}{alias}" for alias in restricted_aliases]
    
    return not Link.objects.filter(short_link__in=restricted_urls)
