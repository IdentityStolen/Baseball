from rest_framework import serializers
from .models import Player

ALLOWED_POSITIONS = ["LF", "RF", "CF", "1B", "2B", "3B", "SS", "C", "DH", "P", "OF"]


class PlayerSerializer(serializers.ModelSerializer):
    batting_average = serializers.DecimalField(
        max_digits=5,
        decimal_places=3,
        allow_null=True,
        required=False,
        coerce_to_string=False,
    )
    on_base_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=3,
        allow_null=True,
        required=False,
        coerce_to_string=False,
    )
    slugging_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=3,
        allow_null=True,
        required=False,
        coerce_to_string=False,
    )
    on_base_plus_slugging = serializers.DecimalField(
        max_digits=6,
        decimal_places=3,
        allow_null=True,
        required=False,
        coerce_to_string=False,
    )

    class Meta:
        model = Player
        fields = [
            "id",
            "name",
            "position",
            "games",
            "at_bat",
            "runs",
            "hits",
            "doubles",
            "triples",
            "home_runs",
            "rbi",
            "walks",
            "strikeouts",
            "stolen_bases",
            "caught_stealing",
            "batting_average",
            "on_base_percentage",
            "slugging_percentage",
            "on_base_plus_slugging",
        ]


class PlayerUpdateSerializer(serializers.ModelSerializer):
    position = serializers.ChoiceField(choices=ALLOWED_POSITIONS)

    # Constants derived from dataset and prior rules
    INT_LIMITS = {
        "games": (0, 3500),
        "at_bat": (0, 14053),
        "hits": (0, 4256),
        "doubles": (8, 746),
        "triples": (4, 177),
        "home_runs": (117, 762),
        "rbi": (418, 2499),
        "walks": (183, 2558),
        "strikeouts": (183, 2597),
        "stolen_bases": (1, 808),
        "caught_stealing": (0, 149),
    }
    FLOAT_LIMITS = {
        "batting_average": (0.231, 0.43),
        "slugging_percentage": (0.34, 0.69),
        "on_base_plus_slugging": (0.671, 1.164),
    }

    class Meta:
        model = Player
        # name is read-only (not editable)
        read_only_fields = ["name"]
        fields = [
            "position",
            "games",
            "at_bat",
            "hits",
            "doubles",
            "triples",
            "home_runs",
            "rbi",
            "walks",
            "strikeouts",
            "stolen_bases",
            "caught_stealing",
            "batting_average",
            "slugging_percentage",
            "on_base_plus_slugging",
        ]

    def validate(self, attrs):
        errors = {}
        for field, (minv, maxv) in self.INT_LIMITS.items():
            if field in attrs and attrs[field] is not None:
                try:
                    val = int(attrs[field])
                except Exception:
                    errors[field] = "must be an integer"
                    continue
                if not (minv <= val <= maxv):
                    errors[field] = f"must be between {minv} and {maxv}"
        for field, (minv, maxv) in self.FLOAT_LIMITS.items():
            if field in attrs and attrs[field] is not None:
                try:
                    val = float(attrs[field])
                except Exception:
                    errors[field] = "must be a number"
                    continue
                if not (minv <= val <= maxv):
                    errors[field] = f"must be between {minv} and {maxv}"
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def update(self, instance: Player, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
