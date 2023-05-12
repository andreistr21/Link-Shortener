from .models import Link


def is_link_free(absolute_uri, alias):
    link = f"{absolute_uri}{alias}"
    
    return not Link.objects.filter(short_link=link).exists()
