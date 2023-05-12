from django.contrib import admin

from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ["user_profile", "short_link", "created_at"]
    ordering = ["-created_at"]
