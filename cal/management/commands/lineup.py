# cal/management/commands/lineup.py
import csv
from django.core.management.base import BaseCommand
from cal.models import Lineup, Game, Hitter, Pitcher, Stadium
from django.conf import settings

def norm_id(v):
    s = str(v).strip()
    if not s or s.lower() == 'nan' or s == '1':
        return None
    # '51868.0' 같은 값 방지
    if s.endswith('.0'):
        s = s[:-2]
    return s

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        csv_file_path = settings.BASE_DIR / 'data' / 'lineups.csv'
        with open(csv_file_path, encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            count = 0
            print(reader.fieldnames)
            for row in reader:
                # game / stadium
                game_pk = norm_id(row['game_id'])
                if not game_pk:
                    continue
                game_obj = Game.objects.get(pk=str(game_pk))

                stadium_name = (row.get('stadium') or '').strip()
                stadium_obj = Stadium.objects.get(stadium=stadium_name)

                # hitter / pitcher (없으면 None)
                h_id = norm_id(row['hitter_id'])
                p_id = norm_id(row['pitcher_id'])
                hitter_obj = Hitter.objects.filter(pk=h_id).first() if h_id else None
                pitcher_obj = Pitcher.objects.filter(pk=p_id).first() if p_id else None

                # 타자/투수 둘 다 없으면 스킵
                if hitter_obj is None and pitcher_obj is None:
                    continue

                # 타순
                try:
                    bo = int(str(row['batting_order']).strip().split('.')[0])
                except Exception:
                    bo = 0

                print(game_obj, hitter_obj or '—', pitcher_obj or '—', bo, stadium_obj)

                obj, created = Lineup.objects.update_or_create(
                    batting_order=bo,
                    game=game_obj,
                    hitter=hitter_obj,
                    pitcher=pitcher_obj,
                    stadium=stadium_obj,
                    defaults={}
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'{count} lineups imported or updated.'))