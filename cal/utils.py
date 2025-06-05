from datetime import datetime, timedelta
from calendar import HTMLCalendar
from django.templatetags.static import static
from .models import Game

class Calendar(HTMLCalendar):
    def __init__(self, year, month, team=None):
        super().__init__()
        self.year = year
        self.month = month
        self.team = team

    def get_opponent(self, game):
        if self.team == game.team1:
            return game.team2
        else:
            return game.team1

    def get_month_data(self):
        # 경기 필터링
        if self.team:
            games1 = Game.objects.filter(date__year=self.year, date__month=self.month, team1=self.team)
            games2 = Game.objects.filter(date__year=self.year, date__month=self.month, team2=self.team)
            games = games1 | games2
        else:
            games = Game.objects.filter(date__year=self.year, date__month=self.month)

        # 날짜별 경기 매핑
        games_by_day = {}
        for game in games:
            day = game.date.day
            id = game.id

            if day not in games_by_day:
                games_by_day[day] = []
            # 팀이 지정된 경우, 해당 팀의 결과만 표시
            if self.team == game.team1:
                result = game.team1_result
            elif self.team == game.team2:
                result = game.team2_result
            else:
                result = ''

            games_by_day[day].append({
                'opponent': self.get_opponent(game),
                'img_url': static(f'cal/images/team/{self.get_opponent(game)}.svg'),
                'time': game.time.strftime("%H:%M") if game.time else "",
                'result': result,
                'id': id,
            })

        # 달력 주차별 데이터
        weeks = []
        for week in self.monthdays2calendar(self.year, self.month):
            week_data = []
            for day, weekday in week:
                week_data.append({
                    'day': day,
                    'games': games_by_day.get(day, []) if day != 0 else [],
                })
            weeks.append(week_data)

        # 요일 헤더
        week_header = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

        return {
            'year': self.year,
            'month': self.month,
            'weeks': weeks,
            'week_header': week_header,
        }