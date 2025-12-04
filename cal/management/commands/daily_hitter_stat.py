import csv
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from cal.models import Hitter_Daily, Game, Hitter


class Command(BaseCommand):
    def _int_or_zero(self, value):
        text = (value or "").strip()
        return int(text) if text else 0

    def handle(self, *args, **kwargs):
        data_dir = settings.BASE_DIR / "data" / "2025"
        file_path = data_dir / "hitters_records.csv"
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            total, success, failed = 0, 0, 0
            for row in reader:
                total += 1
                try:
                    game = Game.objects.get(id=int(row["game_id"]))
                    player_id = Hitter.objects.get(pk=(row["player_id"] or "").strip())
                except Game.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"??Game ID {row['game_id']} ?�음 ??건너?�"))
                    failed += 1
                    continue
                except Hitter.DoesNotExist:
                    failed += 1
                    continue
                try:
                    Hitter_Daily.objects.create(
                        game_id=game,
                        date=datetime.datetime.strptime(row["date"], "%Y%m%d").date(),
                        player=player_id,
                        team=row["team"],
                        AB=self._int_or_zero(row["AB"]),
                        R=self._int_or_zero(row["R"]),
                        H=self._int_or_zero(row["H"]),
                        RBI=self._int_or_zero(row["RBI"]),
                        HR=self._int_or_zero(row["HR"]),
                        BB=self._int_or_zero(row["BB"]),
                        SO=self._int_or_zero(row["SO"]),
                        SB=self._int_or_zero(row["SB"]),
                    )
                    success += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"???�???�패: {e}"))
                    failed += 1

        self.stdout.write(self.style.SUCCESS(f"완료: {success}건 저장 {failed}건 실패 (총{total})"))
