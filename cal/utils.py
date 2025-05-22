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
            return '<td class="border border-gray-300 h-24 align-top"></td>'
        games_per_day = games.filter(date__day=day)
        d = ''
        for game in games_per_day:
            opponent = self.get_opponent(game)
            img_url = static(f'images/team/{opponent}.svg')
            time_str = game.time.strftime("%H:%M") if game.time else ""
            d += f"""
            <div class="mt-1 flex items-center space-x-1">
                <img src="{img_url}" alt="{opponent}" class="h-6 inline-block" title="{opponent}">
                <span class="text-xs text-gray-600">{time_str}</span>
            </div>
            """
        return f'<td class="border border-gray-300 h-24 align-top p-1 text-sm"><span class="font-bold">{day}</span>{d}</td>'


    def formatweek(self, theweek, games):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, games)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        from calendar import monthrange

        # 경기 필터링
        if self.team:
            games1 = Game.objects.filter(date__year=self.year, date__month=self.month, team1=self.team)
            games2 = Game.objects.filter(date__year=self.year, date__month=self.month, team2=self.team)
            games = games1 | games2
        else:
            games = Game.objects.filter(date__year=self.year, date__month=self.month)

        # 지난달/다음달 계산
        if self.month == 1:
            prev_year = self.year - 1
            prev_month = 12
        else:
            prev_year = self.year
            prev_month = self.month - 1

        if self.month == 12:
            next_year = self.year + 1
            next_month = 1
        else:
            next_year = self.year
            next_month = self.month + 1

        prev = f"day={prev_year}-{prev_month}-1"
        next = f"day={next_year}-{next_month}-1"

        # 달력 HTML 시작
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'

        # 네비게이션 행을 달력의 첫 번째 행으로 추가
        cal = f"""
        <table class="w-full table-fixed border-collapse">
            <thead>
                <tr>
                    <th colspan="7" class="text-center py-4">
                        <div class="flex justify-between items-center">
                            <a href="?{prev}" class="text-sm text-gray-600 hover:text-blue-500">← 지난달</a>
                            <span class="text-xl font-bold text-gray-800">{self.year}년 {self.month}월</span>
                            <a href="?{next}" class="text-sm text-gray-600 hover:text-blue-500">다음달 →</a>
                        </div>
                    </th>
                </tr>
            </thead>
        <tbody>
        """

        # 요일 헤더
        cal += f'{self.formatweekheader()}\n'

        # 주차별 날짜 출력
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, games)}\n'

        cal += '</table>'
        return cal
