from django.db import models

class Player(models.Model):
    """Model representing a baseball player's career batting statistics.

    Fields are mapped from the provided JSON structure. Assumptions:
    - "third baseman" in the source JSON is interpreted as "triples" (3B).
    - Percentage fields (AVG, OBP, SLG, OPS) are stored as Decimal with 3 decimal places.
    """

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=10, blank=True, null=True)

    games = models.PositiveIntegerField(blank=True, null=True)
    at_bat = models.PositiveIntegerField(blank=True, null=True)
    runs = models.PositiveIntegerField(blank=True, null=True)
    hits = models.PositiveIntegerField(blank=True, null=True)

    doubles = models.PositiveIntegerField(blank=True, null=True)
    triples = models.PositiveIntegerField(blank=True, null=True)  # mapped from "third baseman"
    home_runs = models.PositiveIntegerField(blank=True, null=True)

    rbi = models.PositiveIntegerField("Runs batted in", blank=True, null=True)
    walks = models.PositiveIntegerField(blank=True, null=True)
    strikeouts = models.PositiveIntegerField(blank=True, null=True)

    stolen_bases = models.PositiveIntegerField(blank=True, null=True)
    caught_stealing = models.PositiveIntegerField(blank=True, null=True)

    # Batting rate stats
    batting_average = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    on_base_percentage = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    slugging_percentage = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    on_base_plus_slugging = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-hits", "-home_runs"]
        verbose_name = "Player"
        verbose_name_plural = "Players"
        indexes = [
            models.Index(fields=["name"], name="player_name_idx"),
            models.Index(fields=["hits"], name="player_hits_idx"),
            models.Index(fields=["home_runs"], name="player_hr_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.position})" if self.position else self.name
