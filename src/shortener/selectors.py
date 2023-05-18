from .models import Link


def is_alias_free(alias: str) -> bool:
    return not Link.objects.filter(alias=alias).exists()
