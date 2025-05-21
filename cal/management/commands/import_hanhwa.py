from django.core.management.base import BaseCommand
import csv
from datetime import datetime
from cal.models import Game  # Game 모델 경로 확인하고 맞게 바꿔

class Command(BaseCommand):
    help = 'Import Hanwha team games from CSV file into DB'

    def handle(self, *args, **kwargs):
        # CSV 파일 경로 적절히 수정하기 (manage.py가 있는 경로 기준)
        Game.objects.filter(home_team='한화').delete()
        csv_file_path = 'data/kbo_schedule.csv'

        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                # team 컬럼에 '한화'만 필터링
                if row['team'] == '한화':
                 
                    # 날짜 문자열을 datetime.date 객체로 변환
                    game_date = datetime.strptime(row['day'], '%Y-%m-%d').date()

                    # Game 객체 생성 - 필드 이름과 타입은 너의 models.py에 맞게 변경
                    game = Game(
                        date=game_date,
                        home_team = row ['team'],
                        away_team=row['opponent'],
                        stadium=row['stadium'],
                        time=row['time'],  # 시간 형식이 맞는지 확인 필요
                        play = row['play'],
                        note = row['note'],
                        result = row['result']
                    )
                    game.save()
                    count += 1

            self.stdout.write(self.style.SUCCESS(f'한화 경기 {count}개를 DB에 저장 완료!'))