from django.urls import path
from . import views

urlpatterns = [
    path("players/by-hits/", views.players_by_hits, name="players-by-hits"),
    path(
        "players/<int:pk>/description/",
        views.player_description,
        name="player-description",
    ),
    path("players/<int:pk>/update/", views.player_update, name="player-update"),
]
