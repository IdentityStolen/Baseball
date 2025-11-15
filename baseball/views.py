from .models import Player
import os
import requests
import logging
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PlayerSerializer, PlayerUpdateSerializer

logger = logging.getLogger("baseball")


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
    """Call OpenAI ChatCompletion API (gpt-4.1) if OPENAI_API_KEY is set. Returns the generated text or raises on error."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OpenAI API key not configured")
    else:
        logger.info(f"API Key loaded correctly!")

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
    logger.info(f"OpenAI payload: {payload}")
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    logger.info(f"OpenAI raw response: {resp.text}")
    resp.raise_for_status()
    data = resp.json()
    # Extract assistant reply
    if "choices" not in data or not data["choices"]:
        logger.error(f"OpenAI error or empty choices: {data}")
        raise RuntimeError(f"OpenAI error or empty choices: {data}")
    try:
        llm_output = data["choices"][0]["message"]["content"]
        logger.info(f"LLM output: {llm_output}")
        return llm_output
    except Exception as e:
        logger.error(f"Exception parsing OpenAI response: {e}, data: {data}")
        raise RuntimeError(f"Invalid response from OpenAI: {e}, data: {data}")


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


class PlayersByHitsAPIView(APIView):
    def get(self, request):
        qs = Player.objects.all().order_by("-hits")
        data = PlayerSerializer(qs, many=True).data
        # DRF's Response handles JSON by default
        return Response({"players": data}, status=status.HTTP_200_OK)


class PlayerDescriptionAPIView(APIView):
    def get(self, request, pk: int):
        try:
            player = Player.objects.get(pk=pk)
        except Player.DoesNotExist:
            return Response(
                {"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND
            )

        prompt = _build_prompt(player)
        try:
            try:
                text = _call_openai(prompt)
                logger.info(
                    f"LLM used for player description: id={player.pk}, name={player.name}, date={date.today()}"
                )
            except Exception:
                text = _fallback_description(player)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"id": player.pk, "description": text}, status=status.HTTP_200_OK
        )


class PlayerUpdateAPIView(APIView):
    def put(self, request, pk: int):
        try:
            player = Player.objects.get(pk=pk)
        except Player.DoesNotExist:
            return Response(
                {"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = PlayerUpdateSerializer(player, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
