from django.core.management.base import BaseCommand
import csv
from datetime import datetime
from cal.models import Game
from django.conf import settings

class Command(BaseCommand):
    help = 'Import all KBO games from CSV file into DB (update if exists)'

    def handle(self, *args, **kwargs):
        csv_file_path = settings.BASE_DIR / 'data' / 'kbo_schedule.csv'
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            count_created = 0
            count_updated = 0
            for row in reader:
                game_date = datetime.strptime(row['day'], '%Y.%m.%d').date()
                try:
                    game_time = datetime.strptime(row['time'], '%H:%M').time()
                except (ValueError, KeyError):
                    game_time = None

                # 기준: 날짜, 팀1, 팀2, 경기장으로 고유 식별
                obj, created = Game.objects.get_or_create(
                    date=game_date,
                    team1=row['team1'],
                    team2=row['team2'],
                    stadium=row['stadium'],
                    defaults={
                        'time': game_time,
                        'team1_score': int(row['team1_score']) if row.get('team1_score') else None,
                        'team2_score': int(row['team2_score']) if row.get('team2_score') else None,
                        'team1_result': row.get('team1_result', ''),
                        'team2_result': row.get('team2_result', ''),
                        'note': row.get('note', '')
                    }
                )
                if not created:
                    # 이미 있으면 업데이트
                    obj.time = game_time
                    obj.team1_score = int(row['team1_score']) if row.get('team1_score') else None
                    obj.team2_score = int(row['team2_score']) if row.get('team2_score') else None
                    obj.team1_result = row.get('team1_result', '')
                    obj.team2_result = row.get('team2_result', '')
                    obj.note = row.get('note', '')
                    obj.save()
                    count_updated += 1
                else:
                    count_created += 1
        self.stdout.write(self.style.SUCCESS(
            f'KBO 전체 경기 {count_created}개 생성, {count_updated}개 업데이트 완료!'
        ))