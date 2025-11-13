from django.http import JsonResponse
from .models import Player


def players_by_hits(request):
    """Return a JSON response with players ordered by hits (descending)."""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    qs = Player.objects.all().order_by("-hits")
    players = []
    for p in qs:
        players.append(
            {
                "name": p.name,
                "position": p.position,
                "games": p.games,
                "at_bat": p.at_bat,
                "runs": p.runs,
                "hits": p.hits,
                "doubles": p.doubles,
                "triples": p.triples,
                "home_runs": p.home_runs,
                "rbi": p.rbi,
                "walks": p.walks,
                "strikeouts": p.strikeouts,
                "stolen_bases": p.stolen_bases,
                "caught_stealing": p.caught_stealing,
                "batting_average": (
                    float(p.batting_average) if p.batting_average is not None else None
                ),
                "on_base_percentage": (
                    float(p.on_base_percentage)
                    if p.on_base_percentage is not None
                    else None
                ),
                "slugging_percentage": (
                    float(p.slugging_percentage)
                    if p.slugging_percentage is not None
                    else None
                ),
                "on_base_plus_slugging": (
                    float(p.on_base_plus_slugging)
                    if p.on_base_plus_slugging is not None
                    else None
                ),
            }
        )

    return JsonResponse({"players": players}, safe=False)
