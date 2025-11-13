import requests
from django.core.management.base import BaseCommand
from baseball.models import Player

API_URL = "https://api.hirefraction.com/api/test/baseball"

FIELD_MAP = {
    "Player name": "name",
    "position": "position",
    "Games": "games",
    "At-bat": "at_bat",
    "Runs": "runs",
    "Hits": "hits",
    "Double (2B)": "doubles",
    "third baseman": "triples",
    "home run": "home_runs",
    "run batted in": "rbi",
    "a walk": "walks",
    "Strikeouts": "strikeouts",
    "stolen base": "stolen_bases",
    "Caught stealing": "caught_stealing",
    "AVG": "batting_average",
    "On-base Percentage": "on_base_percentage",
    "Slugging Percentage": "slugging_percentage",
    "On-base Plus Slugging": "on_base_plus_slugging",
}

class Command(BaseCommand):
    help = "Load players from API endpoint into Player model"

    def handle(self, *args, **options):
        self.stdout.write(f"Fetching player data from {API_URL} ...")
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.stderr.write(f"Failed to fetch data: {e}")
            return

        if not isinstance(data, list):
            self.stderr.write("API response is not a list of players.")
            return

        created, updated, errors = 0, 0, 0
        for entry in data:
            player_data = {}
            for api_field, model_field in FIELD_MAP.items():
                player_data[model_field] = entry.get(api_field)
            try:
                obj, created_flag = Player.objects.update_or_create(
                    name=player_data["name"], defaults=player_data
                )
                if created_flag:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
                self.stderr.write(f"Error saving player {player_data.get('name')}: {e}")
        self.stdout.write(f"Done. Created: {created}, Updated: {updated}, Errors: {errors}")
