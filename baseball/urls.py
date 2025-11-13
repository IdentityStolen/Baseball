from django.urls import path
from . import views

urlpatterns = [
    path("players/by-hits/", views.players_by_hits, name="players-by-hits"),
]
