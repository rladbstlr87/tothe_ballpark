from django.core.management.base import BaseCommand
import csv
from datetime import datetime
from cal.models import Game
from django.conf import settings

class Command(BaseCommand):
    help = 'Import all KBO games from CSV file into DB'

    def handle(self, *args, **kwargs):
        csv_file_path = settings.BASE_DIR / 'data' / 'kbo_schedule.csv'
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                game_date = datetime.strptime(row['day'], '%Y.%m.%d').date()
                try:
                    game_time = datetime.strptime(row['time'], '%H:%M').time()
                except (ValueError, KeyError):
                    game_time = None
                game = Game(
                    date=game_date,
                    time=game_time,
                    team1=row['team1'],
                    team2=row['team2'],
                    team1_score=int(row['team1_score']) if row.get('team1_score') else None,
                    team2_score=int(row['team2_score']) if row.get('team2_score') else None,
                    team1_result=row.get('team1_result', ''),
                    team2_result=row.get('team2_result', ''),
                    stadium=row['stadium'],
                    note=row.get('note', '')
                )
                game.save()
                count += 1
        self.stdout.write(self.style.SUCCESS(f'KBO 전체 경기 {count}개를 DB에 저장 완료!'))