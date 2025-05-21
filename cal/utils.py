from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Game

class Calendar(HTMLCalendar):
    def __init__(self, year, month, team=None):
        super().__init__()
        self.year = year
        self.month = month
        self.team = team

    def formatday(self, day, games):
        if day == 0:
            return '<td></td>'
        games_per_day = games.filter(date__day=day)
        d = ''
        for game in games_per_day:
            d += f'<li>{game.home_team} vs {game.away_team} {game.time}</li>'
        return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"

    def formatweek(self, theweek, games):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, games)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        # team이 지정된 경우 해당 팀의 경기만 가져옴
        if self.team:
            games = Game.objects.filter(date__year=self.year, date__month=self.month, home_team=self.team)
        else:
            games = Game.objects.filter(date__year=self.year, date__month=self.month)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, games)}\n'
        cal += '</table>'
        return cal