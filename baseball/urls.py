from django.urls import path
from .views import PlayersByHitsAPIView, PlayerDescriptionAPIView, PlayerUpdateAPIView

urlpatterns = [
    path("players/by-hits/", PlayersByHitsAPIView.as_view(), name="players-by-hits"),
    path(
        "players/<int:pk>/description/",
        PlayerDescriptionAPIView.as_view(),
        name="player-description",
    ),
    path(
        "players/<int:pk>/update/", PlayerUpdateAPIView.as_view(), name="player-update"
    ),
]
