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
        # 로그인 사용자가 team1이면 team2가 상대, 반대도 마찬가지
        if self.team == game.team1:
            return game.team2
        else:
            return game.team1

    def formatday(self, day, games):
        if day == 0:
            return '<td></td>'
        games_per_day = games.filter(date__day=day)
        d = ''
        for game in games_per_day:
            opponent = self.get_opponent(game)
            img_url = static(f'images/team/{opponent}.svg')
            time_str = game.time.strftime("%H:%M") if game.time else ""
            d += (
                f'<img src="{img_url}" alt="{opponent}" style="height:50px;vertical-align:middle;">'
            )
        return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"

    def formatweek(self, theweek, games):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, games)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        if self.team:
            games1 = Game.objects.filter(date__year=self.year, date__month=self.month, team1=self.team)
            games2 = Game.objects.filter(date__year=self.year, date__month=self.month, team2=self.team)
            games = games1 | games2
        else:
            games = Game.objects.filter(date__year=self.year, date__month=self.month)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, games)}\n'
        cal += '</table>'
        return cal