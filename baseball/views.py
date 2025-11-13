from django.http import JsonResponse
from .models import Player
import os
import requests


def players_by_hits(request):
    """Return a JSON response with players ordered by hits (descending)."""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    qs = Player.objects.all().order_by("-hits")
    players = []
    for p in qs:
        players.append(
            {
                "id": p.pk,
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


def _build_prompt(player: Player) -> str:
    """Create a prompt from the player's stats to feed to the LLM."""
    stats = [
        f"Position: {player.position}",
        f"Games: {player.games}",
        f"At-bats: {player.at_bat}",
        f"Runs: {player.runs}",
        f"Hits: {player.hits}",
        f"Doubles: {player.doubles}",
        f"Triples: {player.triples}",
        f"Home runs: {player.home_runs}",
        f"RBIs: {player.rbi}",
        f"Walks: {player.walks}",
        f"Strikeouts: {player.strikeouts}",
        f"Stolen bases: {player.stolen_bases}",
        f"Caught stealing: {player.caught_stealing}",
        f"AVG: {player.batting_average}",
        f"OBP: {player.on_base_percentage}",
        f"SLG: {player.slugging_percentage}",
        f"OPS: {player.on_base_plus_slugging}",
    ]
    stats_text = "\n".join([s for s in stats if s is not None])
    prompt = (
        f"Write a concise, engaging 2-4 sentence biographical description for the baseball player {player.name}.\n"
        f"Use the following career statistics to highlight strengths, playing style, and notable achievements:\n{stats_text}\n"
        "Keep it suitable for display on a stats site; avoid unverifiable claims."
    )
    return prompt


def _call_openai(prompt: str) -> str:
    """Call OpenAI ChatCompletion API (gpt-3.5-turbo) if OPENAI_API_KEY is set. Returns the generated text or raises on error."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OpenAI API key not configured")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that writes short baseball player bios based on statistics.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 150,
        "temperature": 0.7,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    # Extract assistant reply
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Invalid response from OpenAI: {e}")


def _fallback_description(player: Player) -> str:
    """Generate a simple description from stats without calling an LLM."""
    parts = []
    parts.append(f"{player.name} played primarily as {player.position}.")
    if player.hits is not None and player.games is not None:
        parts.append(f"Over {player.games} games, they collected {player.hits} hits.")
    if player.home_runs:
        parts.append(
            f"They hit {player.home_runs} home runs, driving in {player.rbi} runs."
        )
    if player.on_base_plus_slugging:
        parts.append(
            f"Career OPS of {player.on_base_plus_slugging} highlights their offensive impact."
        )
    return " ".join(parts)


def player_description(request, pk):
    """Return a generated description for a player identified by primary key.

    If OPENAI_API_KEY is configured in the environment, the server will call OpenAI's ChatCompletions API. Otherwise it will return a deterministic summary generated from stats.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        player = Player.objects.get(pk=pk)
    except Player.DoesNotExist:
        return JsonResponse({"error": "Player not found"}, status=404)

    prompt = _build_prompt(player)
    try:
        try:
            text = _call_openai(prompt)
        except Exception:
            # Fallback to template-based description when OpenAI is unavailable
            text = _fallback_description(player)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"id": player.pk, "description": text})
