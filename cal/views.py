from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, timedelta, date
from django.utils.safestring import mark_safe
import calendar
from .models import *
from .utils import Calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def index(request):
    return render(request, 'index.html')

@never_cache
@login_required
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

@never_cache
@login_required
def lineup(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    lineups = Lineup.objects.filter(game=game).order_by('id')
    
    has_lineup = lineups.exists()

    user_lineup = []
    opponent_lineup = []
    opponent_team = None

    if has_lineup:
        pitcher_indexes = [i for i, l in enumerate(lineups) if l.batting_order == 1]
        if len(pitcher_indexes) >= 2:
            away_lineup = lineups[pitcher_indexes[0]:pitcher_indexes[0]+10]
            home_lineup = lineups[pitcher_indexes[1]:pitcher_indexes[1]+10]

            user_team = request.user.team
            if user_team == game.team1:
                opponent_team = game.team2
                user_lineup = away_lineup
                opponent_lineup = home_lineup
            else:
                opponent_team = game.team1
                user_lineup = home_lineup
                opponent_lineup = away_lineup
        else:
            has_lineup = False  # 선발투수 부족하면 라인업 없는 걸로 처리
    else:
        user_team = request.user.team
        opponent_team = game.team2 if request.user.team == game.team1 else game.team1
    
    context = {
        'game': game,
        'user_lineup': user_lineup,
        'opponent_lineup': opponent_lineup,
        'user_team': request.user.team,
        'opponent_team': opponent_team,
        'has_lineup': has_lineup,
    }
    return render(request, 'lineup.html', context)

@never_cache
@login_required
def attendance(request, game_id):
    user = request.user
    game = Game.objects.get(id=game_id)

    if user in game.attendance_users.all():
        game.attendance_users.remove(user)
        attended = False
    else:
        game.attendance_users.add(user)
        attended = True

    return JsonResponse({'success': True, 'attended': attended})

@never_cache
@login_required
def user_games(request, user_id):
    user = request.user
    games = user.attendance_game.all().order_by('date', 'time')

    user_team = user.team

    opponent_team = []
    result = []
    for game in games:
        if user_team == game.team1:
            opponent_team.append(game.team2)
            result.append(game.team1_result)
        else:
            opponent_team.append(game.team1)
            result.append(game.team2_result)

    context = {
        'game_data': zip(games, opponent_team, result),
    }
    return render(request, 'user_games.html', context)

def about_us(request):
    return render(request, 'about_us.html')