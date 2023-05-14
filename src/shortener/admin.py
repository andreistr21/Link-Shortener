from django.contrib import admin

from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ["alias", "user_profile" , "created_at"]
    ordering = ["-created_at"]
