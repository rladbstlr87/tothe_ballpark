from django.shortcuts import render, redirect
from datetime import datetime, timedelta, date
from django.utils.safestring import mark_safe
import calendar
from .models import *
from .utils import Calendar
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'index.html')

def calendar_view(request):
    user_team = None
    user_attendance_game_ids = []
    if request.user.is_authenticated:
        user_team = request.user.team
        user_attendance_game_ids = list(request.user.attendance_game.values_list('id', flat=True))
    d = get_date(request.GET.get('day', None))
    cal = Calendar(d.year, d.month, team=user_team)
    cal_data = cal.get_month_data()

    context = {
        'cal_data': cal_data,
        'prev_month': prev_month(d),
        'next_month': next_month(d),
        'user_team': user_team,
        'user_attendance_game_ids': user_attendance_game_ids,
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

def lineup(request, game_id):
    game = Game.objects.get(id=game_id)
    lineups = Lineup.objects.filter(game=game)
    pitchers = lineups.filter(batting_order=1)
    batters = lineups.filter(batting_order__gt=1).order_by('batting_order') # __gt=1 1보다 큰 숫자들
    user_team = request.user.team
    context = {
        'game': game,
        'lineups': lineups,
        'pitchers': pitchers,
        'batters': batters,
        'user_team': user_team,
    }
    return render(request, 'lineup.html', context)

@login_required
def attendance(request, game_id):
    user = request.user
    game = Game.objects.get(id=game_id)

    if user in game.attendance_users.all():
        game.attendance_users.remove(user)
    else:
        game.attendance_users.add(user)

    return redirect('cal:lineup', game_id=game_id)