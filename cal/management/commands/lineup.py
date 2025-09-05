# cal/management/commands/lineup.py
import csv
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from cal.models import Lineup, Game, Hitter, Pitcher, Stadium

def norm_id(v):
    s = str(v).strip()
    if not s or s.lower() == 'nan' or s == '1':
        return None
    if s.endswith('.0'):
        s = s[:-2]
    return s

def parse_batting_order(v):
    try:
        return int(str(v).strip().split('.')[0])
    except Exception:
        return 0

def team_of(hitter_obj, pitcher_obj):
    # hitter 우선, 없으면 pitcher에서 팀명
    if hitter_obj and getattr(hitter_obj, "team_name", None):
        return hitter_obj.team_name
    if pitcher_obj and getattr(pitcher_obj, "team_name", None):
        return pitcher_obj.team_name
    return None

class Command(BaseCommand):
    help = "라인업 CSV를 읽어 게임별로 2팀×10 완비 시에만 원자적으로 교체 적재"

    def add_arguments(self, parser):
        parser.add_argument('--only-game', type=str, default=None)
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **kwargs):
        csv_file_path = settings.BASE_DIR / 'data' / 'lineups.csv'
        total_inserted = 0

        # 1) CSV → 게임별 버퍼링 (추가 검증을 위해 모아둠)
        by_game = defaultdict(list)

        with open(csv_file_path, encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                game_pk = norm_id(row.get('game_id'))
                if not game_pk:
                    continue

                bo = parse_batting_order(row.get('batting_order'))

                h_id = norm_id(row.get('hitter_id'))
                p_id = norm_id(row.get('pitcher_id'))
                hitter_obj = Hitter.objects.filter(pk=h_id).first() if h_id else None
                pitcher_obj = Pitcher.objects.filter(pk=p_id).first() if p_id else None

                # 타자/투수 둘 다 없으면 스킵
                if hitter_obj is None and pitcher_obj is None:
                    continue

                stadium_name = (row.get('stadium') or '').strip()
                if not stadium_name:
                    continue
                stadium_obj = Stadium.objects.filter(stadium=stadium_name).first()
                if stadium_obj is None:
                    continue

                by_game[str(game_pk)].append({
                    "bo": bo,
                    "hitter": hitter_obj,
                    "pitcher": pitcher_obj,
                    "stadium": stadium_obj,
                })

        # 2) 게임별로 검증 → 교체 적재(트랜잭션)
        for game_pk, items in by_game.items():
            game = Game.objects.filter(pk=game_pk).first()
            if game is None:
                continue

            # 2-1) 팀별 타순 수집
            team_orders = defaultdict(set)
            rows_normalized = []
            for it in items:
                bo = it["bo"]
                h = it["hitter"]
                p = it["pitcher"]
                tname = team_of(h, p)
                if not tname:
                    # 팀 판단 불가한 레코드는 버림
                    continue

                rows_normalized.append((bo, h, p, tname, it["stadium"]))
                if bo >= 1 and bo <= 10:
                    team_orders[tname].add(bo)

            # 2-2) “정확히 2팀” & 각 팀 “1..10” 완비 여부 확인
            if len(team_orders) != 2:
                # 미완비 → 이 게임은 스킵 (아무 것도 변경하지 않음)
                continue

            complete = True
            for tname, orders in team_orders.items():
                if sorted(orders) != list(range(1, 11)):
                    complete = False
                    break
            if not complete:
                # 미완비 → 스킵
                continue

            # 2-3) 원자적 교체: 기존 삭제 → 신규 20건 일괄 생성
            objs = []
            for bo, h, p, tname, stadium in rows_normalized:
                # 역할 정합성: 1은 투수, 2~10은 타자만
                if bo == 1 and p is None:
                    complete = False
                    break
                if bo >= 2 and bo <= 10 and h is None:
                    complete = False
                    break

                objs.append(Lineup(
                    game=game,
                    batting_order=bo,
                    hitter=h if bo >= 2 else None,
                    pitcher=p if bo == 1 else None,
                    stadium=stadium,
                    # team_name 컬럼을 비정규화해 두었다면 여기에 할당:
                    # team_name=tname,
                ))

            if not complete or len(objs) != 20:
                # 안전망: 정확히 20건이 아닐 경우 커밋하지 않음
                continue

            with transaction.atomic():
                # 경쟁 조건 방지
                Lineup.objects.select_for_update().filter(game=game).delete()
                Lineup.objects.bulk_create(objs, batch_size=100)

            total_inserted += len(objs)

        self.stdout.write(self.style.SUCCESS(f"done. inserted/updated: {total_inserted}"))