from django.shortcuts import render
from datetime import datetime, timedelta, date
from django.utils.safestring import mark_safe
import calendar
import csv
from django.conf import settings
from .models import *
from .utils import Calendar

def index(request):
    return render(request, 'index.html')

def calendar_view(request):
    user_team = None
    if request.user.is_authenticated:
        user_team = request.user.team  # 로그인한 사용자의 팀

        # 기존 일정 삭제 후 새로 저장
        Game.objects.all().delete()
        csv_file_path = settings.BASE_DIR / 'data' / 'kbo_schedule.csv'
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['team'] == user_team:
                    game_date = datetime.strptime(row['day'], '%Y-%m-%d').date()
                    game = Game(
                        date=game_date,
                        home_team=row['team'],
                        away_team=row['opponent'],
                        stadium=row['stadium'],
                        time=row['time'],
                        play=row['play'],
                        note=row['note'],
                        result=row['result']
                    )
                    game.save()

    d = get_date(request.GET.get('day', None))
    cal = Calendar(d.year, d.month, team=user_team)  # team 전달
    html_cal = cal.formatmonth(withyear=True)

    context = {
        'calendar': mark_safe(html_cal),
        'prev_month': prev_month(d),
        'next_month': next_month(d),
        'user_team': user_team,
    }
    return render(request, 'cal/calendar.html', context)

def get_date(req_day):
    try:
        if req_day:
            year, month, day = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
    except (ValueError, TypeError):
        pass
    return datetime.today().date()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    a = 'day=' + str(prev_month.year) + '-' + str(prev_month.month) + '-' + str(prev_month.day)
    return a

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    a = 'day=' + str(next_month.year) + '-' + str(next_month.month) + '-' + str(next_month.day)
    return a