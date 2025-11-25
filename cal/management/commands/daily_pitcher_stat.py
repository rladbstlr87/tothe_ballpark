import csv
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from cal.models import Pitcher_Daily, Game, Pitcher


class Command(BaseCommand):
    def _int_or_zero(self, value):
        text = (value or "").strip()
        return int(text) if text else 0

    def _float_or_zero(self, value):
        text = (value or "").strip()
        return float(text) if text else 0.0

    def handle(self, *args, **kwargs):
        file_path = settings.BASE_DIR / "data" / "pitchers_records.csv"
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            total, success, failed = 0, 0, 0
            for row in reader:
                total += 1
                try:
                    game = Game.objects.get(id=int(row["game_id"]))
                    player_id = Pitcher.objects.get(player_id=row["player_id"])
                except Game.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"??Game ID {row['game_id']} ?�음 ??건너?�"))
                    failed += 1
                    continue

                try:
                    Pitcher_Daily.objects.create(
                        game_id=game,
                        date=datetime.datetime.strptime(row["date"], "%Y%m%d").date(),
                        player=player_id,
                        team=row["team"],
                        IP=self._float_or_zero(row["IP"]),
                        H=self._int_or_zero(row["H"]),
                        R=self._int_or_zero(row["R"]),
                        ER=self._int_or_zero(row["ER"]),
                        BB=self._int_or_zero(row["BB"]),
                        SO=self._int_or_zero(row["SO"]),
                        HR=self._int_or_zero(row["HR"]),
                        BF=self._int_or_zero(row["BF"]),
                        AB=self._int_or_zero(row["AB"]),
                        NP=self._int_or_zero(row["NP"]),
                    )
                    success += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"???�???�패: {e}"))
                    failed += 1

        self.stdout.write(self.style.SUCCESS(f"???�료: {success}�??�?? {failed}�??�패 (�?{total})"))
