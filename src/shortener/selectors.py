from .models import Link


def is_alias_free(alias):
    return not Link.objects.filter(alias=alias).exists()
