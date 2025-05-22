from django.shortcuts import render
from datetime import datetime, timedelta, date
from django.utils.safestring import mark_safe
import calendar
from .models import *
from .utils import Calendar

def index(request):
    return render(request, 'index.html')

def calendar_view(request):
    user_team = None
    if request.user.is_authenticated:
        user_team = request.user.team  # 로그인한 사용자의 팀
    # DB에서 team1 또는 team2에 내가 응원하는 팀이 포함된 경기만 가져오도록 Calendar에 team 전달
    d = get_date(request.GET.get('day', None))
    cal = Calendar(d.year, d.month, team=user_team)  # team 전달
    html_cal = cal.formatmonth(withyear=True)

    context = {
        'calendar': mark_safe(html_cal),
        'prev_month': prev_month(d),
        'next_month': next_month(d),
        'user_team': user_team,
    }
    return render(request, 'calendar.html', context)

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