# Generated to backfill pitchers that appear in lineups/records but are absent
from django.db import migrations


def add_missing_pitchers(apps, schema_editor):
    Pitcher = apps.get_model('cal', 'Pitcher')
    defaults = {
        "player_name": "",
        "team_name": "",
        "ERA": 0.0,
        "G": 0,
        "W": 0,
        "L": 0,
        "SV": 0,
        "HLD": 0,
        "WPCT": 0.0,
        "IP": 0.0,
        "H": 0,
        "HR": 0,
        "BB": 0,
        "HBP": 0,
        "SO": 0,
        "R": 0,
        "ER": 0,
        "WHIP": 0.0,
        "CG": 0,
        "SHO": 0,
        "QS": 0,
        "BSV": 0,
        "TBF": 0,
        "NP": 0,
        "AVG": 0.0,
        "H_2B": 0,
        "H_3B": 0,
        "SAC": 0,
        "SF": 0,
        "IBB": 0,
        "WP": 0,
        "BK": 0,
        "speed": 0,
        "stamina": 0,
        "control": 0.0,
        "fireball": 0.0,
        "style": 0,
    }

    to_create = [
        ("55342", "Pitcher 55342", "WO"),
        ("55646", "Pitcher 55646", "HT"),
        ("53164", "Pitcher 53164", "WO"),
        ("55632", "Pitcher 55632", "HT"),
    ]

    for pid, name, team in to_create:
        Pitcher.objects.get_or_create(
            player_id=pid,
            defaults={**defaults, "player_name": name, "team_name": team},
        )


def remove_missing_pitchers(apps, schema_editor):
    Pitcher = apps.get_model('cal', 'Pitcher')
    Pitcher.objects.filter(player_id__in=["55342", "55646", "53164", "55632"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0003_fix_address_db_column'),
    ]

    operations = [
        migrations.RunPython(add_missing_pitchers, remove_missing_pitchers),
    ]
