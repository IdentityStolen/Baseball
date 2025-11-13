from django.contrib import admin
from .models import Player

# Register your models here.


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "games", "at_bat", "hits", "home_runs", "rbi")
    search_fields = ("name", "position")
    list_filter = ("position",)
