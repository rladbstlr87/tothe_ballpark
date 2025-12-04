import csv
from datetime import datetime
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings
from cal.models import Game, Hitter, Pitcher


def _parse_time(value):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except Exception:
        return None


def _parse_int(value):
    try:
        return int(value)
    except Exception:
        return None


class Command(BaseCommand):
    help = "lineups.csv를 기준으로 game_id를 맞춰 Game 테이블을 생성/업데이트"

    def handle(self, *args, **kwargs):
        data_dir = settings.BASE_DIR / "data" / "2025"
        lineups_path = data_dir / "lineups.csv"
        schedule_path = data_dir / "kbo_schedule.csv"

        # 1) 스케줄 로드 후 (date, stadium, teams) 키로 색인
        schedule_by_key = defaultdict(list)
        schedule_by_date_stadium = defaultdict(list)
        with open(schedule_path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                date_str = row["day"].replace(".", "")
                teams = frozenset([row["team1"], row["team2"]])
                key = (date_str, row["stadium"], teams)
                schedule_by_key[key].append(row)
                schedule_by_date_stadium[(date_str, row["stadium"])].append(row)

        # 2) lineups.csv에서 game_id별로 날짜/구장/팀 추출
        lineup_info = {}
        with open(lineups_path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                gid = row.get("game_id")
                if not gid or not gid.isdigit():
                    continue
                gid = int(gid)
                date_str = row.get("date", "")
                stadium = row.get("stadium", "")
                info = lineup_info.setdefault(
                    gid, {"date": date_str, "stadium": stadium, "teams": set()}
                )

                hitter_id = (row.get("hitter_id") or "").strip()
                pitcher_id = (row.get("pitcher_id") or "").strip()
                if hitter_id and hitter_id != "1":
                    hitter = Hitter.objects.filter(pk=hitter_id).first()
                    if hitter and hitter.team_name:
                        info["teams"].add(hitter.team_name)
                if pitcher_id and pitcher_id != "1":
                    pitcher = Pitcher.objects.filter(pk=pitcher_id).first()
                    if pitcher and pitcher.team_name:
                        info["teams"].add(pitcher.team_name)

        created, updated, skipped = 0, 0, 0

        # 3) game_id 기준으로 Game 생성/업데이트
        for gid, info in lineup_info.items():
            date_str = info["date"]
            stadium = info["stadium"]
            teams = frozenset(info["teams"])

            schedule_rows = schedule_by_key.get((date_str, stadium, teams), [])
            schedule_row = None
            if schedule_rows:
                schedule_rows.sort(key=lambda r: r.get("time") or "")
                schedule_row = schedule_rows[0]
            if schedule_row is None:
                candidates = schedule_by_date_stadium.get((date_str, stadium), [])
                candidates.sort(key=lambda r: r.get("time") or "")
                schedule_row = candidates[0] if candidates else None

            if schedule_row:
                team1 = schedule_row["team1"]
                team2 = schedule_row["team2"]
                game_time = _parse_time(schedule_row.get("time", ""))
                team1_score = _parse_int(schedule_row.get("team1_score", ""))
                team2_score = _parse_int(schedule_row.get("team2_score", ""))
                team1_result = schedule_row.get("team1_result", "")
                team2_result = schedule_row.get("team2_result", "")
                note = schedule_row.get("note", "")
            else:
                if len(teams) == 2:
                    team1, team2 = sorted(list(teams))
                else:
                    skipped += 1
                    continue
                game_time = None
                team1_score = None
                team2_score = None
                team1_result = ""
                team2_result = ""
                note = ""

            defaults = {
                "date": datetime.strptime(date_str, "%Y%m%d").date(),
                "time": game_time,
                "team1": team1,
                "team2": team2,
                "team1_score": team1_score,
                "team2_score": team2_score,
                "team1_result": team1_result,
                "team2_result": team2_result,
                "stadium": stadium,
                "note": note,
            }

            obj, created_flag = Game.objects.update_or_create(
                pk=gid,
                defaults=defaults,
            )
            if created_flag:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Game 동기화 완료: {created} 생성, {updated} 업데이트, {skipped} 스킵"
            )
        )
