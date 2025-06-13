from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from datetime import datetime, timedelta, date
from collections import defaultdict
from .models import *
from accounts.models import User
from .utils import Calendar
import calendar
import random

# 홈페이지
def index(request):
    backgrounds = [
        'cal/images/bg/home0.png',
        'cal/images/bg/home1.png',
        'cal/images/bg/home2.png',
    ]
    mobile_backgrounds = [
        'cal/images/bg/mobile0.png',
        'cal/images/bg/mobile1.png',
        'cal/images/bg/mobile2.png',
    ]
        
    chosen_background = random.choice(backgrounds)
    chosen_mobile_background = random.choice(mobile_backgrounds)
    context = {
        'random_bg': chosen_background,
        'random_mobile_bg': chosen_mobile_background,
    }

    return render(request, 'index.html', context)

# 캘린더 메인 뷰
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

# 날짜 유틸 함수
def get_date(req_day):
    try:
        if req_day:
            year, month, day = (int(x) for x in req_day.split('-'))
            return date(year, month, 1)
    except (ValueError, TypeError):
        pass
    return datetime.today().date()

def prev_month(d):
    first = d.replace(day=1)
    prev = first - timedelta(days=1)
    return f'day={prev.year}-{prev.month}-{prev.day}'

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_ = last + timedelta(days=1)
    return f'day={next_.year}-{next_.month}-{next_.day}'

# 키플레이어 함수
def calculate_hitter_score(h):
    return (
        h.RBI * 3 +
        h.R * 1.5 +
        h.HR * 3.5 +
        h.H * 1.2 +
        h.BB * 0.7 +
        h.SB * 1.0 -
        h.SO * 1.0
    )

def calculate_pitcher_score(p):
    return (
        p.IP * 3 -
        p.ER * 2.5 -
        p.H * 0.5 -
        p.BB * 0.7 -
        p.HR * 2.0 -
        p.R * 1.0 +
        p.SO * 1.0
    )

# 라인업 뷰
@never_cache
@login_required
def lineup(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    lineups = Lineup.objects.filter(game=game).order_by('id')
    has_lineup = lineups.exists()

    user_lineup = []
    opponent_lineup = []
    opponent_team = None

    # 타자 기록
    all_hitter_qs = Hitter_Daily.objects.all().order_by('-date')
    latest_daily_stats = {}
    for record in all_hitter_qs:
        if record.player_id not in latest_daily_stats:
            latest_daily_stats[record.player_id] = record

    today_hitter_records = Hitter_Daily.objects.filter(game_id=game).order_by('-date')
    for record in today_hitter_records:
        latest_daily_stats[record.player_id] = record

    # 투수 기록
    all_pitcher_qs = Pitcher_Daily.objects.all().order_by('-date')
    latest_pitcher_stats = {}
    for record in all_pitcher_qs:
        if record.player_id not in latest_pitcher_stats:
            latest_pitcher_stats[record.player_id] = record

    today_pitcher_records = Pitcher_Daily.objects.filter(game_id=game).order_by('-date')
    for record in today_pitcher_records:
        latest_pitcher_stats[record.player_id] = record

    # 라인업 분기
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
            has_lineup = False
    else:
        user_team = request.user.team
        opponent_team = game.team2 if user_team == game.team1 else game.team1

    # 점수 처리
    if request.user.team == game.team1:
        user_score = game.team1_score
        opponent_score = game.team2_score
    else:
        user_score = game.team2_score
        opponent_score = game.team1_score

    # 경기 후 여부
    is_after_game = (game.team1_score is not None) and (game.team2_score is not None)

    stadium_ticket = game.stadium

    if game.team2 == 'LG' and game.stadium == '잠실':
        stadium_ticket = '잠실LG'

    if game.team2 == 'OB' and game.stadium == '잠실':
        stadium_ticket = '잠실OB'

    ticket = {
        "대전(신)": "https://www.ticketlink.co.kr/sports/137/63",
        "수원": "https://www.ticketlink.co.kr/sports/137/62",
        "광주": "https://www.ticketlink.co.kr/sports/137/58",
        "대구": "https://www.ticketlink.co.kr/sports/137/57",
        '포항': "https://www.ticketlink.co.kr/sports/137/57",
        "잠실LG": "https://www.ticketlink.co.kr/sports/137/59",
        "문학": "https://www.ticketlink.co.kr/sports/137/476",
        "고척": "https://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode=07001&TeamCode=PB003",
        "잠실OB": "https://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode=07001&TeamCode=PB004",
        "사직": "https://ticket.giantsclub.com/loginForm.do",
        "창원": "https://ticket.ncdinos.com/games",
        '울산': "https://ticket.ncdinos.com/games",
    }

    # 수훈선수
    hitters = Hitter_Daily.objects.filter(game_id=game)
    pitchers = Pitcher_Daily.objects.filter(game_id=game)

    best_hitter = max(hitters, key=calculate_hitter_score, default=None)
    best_pitcher = max(pitchers, key=calculate_pitcher_score, default=None)
    
    hitter_score = calculate_hitter_score(best_hitter) if best_hitter else -999
    pitcher_score = calculate_pitcher_score(best_pitcher) if best_pitcher else -999

    if hitter_score >= pitcher_score and best_hitter:
        best_player = best_hitter
        player_type = "타자"
        score = hitter_score
        try:
            best_player_name = Hitter.objects.get(player_id=best_player.player_id).player_name
        except Hitter.DoesNotExist:
            best_player_name = "-"
    elif best_pitcher:
        best_player = best_pitcher
        player_type = "투수"
        score = pitcher_score
        try:
            best_player_name = Pitcher.objects.get(player_id=best_player.player_id).player_name
        except Pitcher.DoesNotExist:
            best_player_name = "-"
    else:
        # 둘 다 없을 경우 예외 처리
        best_player = None
        best_player_name = "-"
        player_type = "-"
        score = 0

    context = {
        'game': game,
        'user_lineup': user_lineup,
        'opponent_lineup': opponent_lineup,
        'user_team': request.user.team,
        'opponent_team': opponent_team,
        'has_lineup': has_lineup,
        'latest_daily_stats': latest_daily_stats,
        'latest_pitcher_stats': latest_pitcher_stats,
        'today': game.date,
        'user_score': user_score,
        'opponent_score': opponent_score,
        'is_after_game': is_after_game,
        'ticket_url': ticket[stadium_ticket],
        'best_player': best_player,
        'best_player_name': best_player_name,
        'player_type': player_type,
        'score': round(score, 2),
    }

    return render(request, 'lineup.html', context)

# 직관 체크
@never_cache
@login_required
def attendance(request, game_id):
    user = request.user
    game = get_object_or_404(Game, id=game_id)

    if user in game.attendance_users.all():
        game.attendance_users.remove(user)
        attended = False
    else:
        game.attendance_users.add(user)
        attended = True

    return JsonResponse({'success': True, 'attended': attended})

# 사용자 직관한 경기 리스트
@never_cache
@login_required
def user_games(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        return redirect('cal:calendar')
    games = user.attendance_game.all().order_by('date', 'time')

    win_count = 0
    lose_count = 0
    raw_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0})
    user_team = request.user.team
    for game in games:
        stadium = game.stadium

        if game.team1 == user_team:
            result = game.team1_result
        elif game.team2 == user_team:
            result = game.team2_result
        else:
            continue  # 예외적인 경우 방지

        raw_stats[stadium]['total'] += 1
        if result == '승':
            raw_stats[stadium]['wins'] += 1
            win_count += 1
        elif result == '패':
            raw_stats[stadium]['losses'] += 1
            lose_count += 1

    stadium_stats = [
        {
            'stadium': stadium,
            'wins': stats['wins'],
            'losses': stats['losses'],
            'total': stats['total'],
            'percent': round((stats['wins'] / stats['total']) * 100, 1) if stats['total'] > 0 else 0.0
        }
        for stadium, stats in raw_stats.items()
    ]

    TEAM_NAME = {
        'LT': '롯데 자이언츠',
        'HT': '기아 타이거즈',
        'LG': 'LG 트윈스',
        'OB': '두산 베어스',
        'SK': 'SSG 랜더스',
        'WO': '키움 히어로즈',
        'SS': '삼성 라이온즈',
        'HH': '한화 이글스',
        'KT': 'KT 위즈',
        'NC': 'NC 다이노스',
    }

    opponent_team = []
    result = []

    for game in games:
        if user_team == game.team1:
            opponent_team.append(TEAM_NAME.get(game.team2, game.team2))
            result.append(game.team1_result)
        else:
            opponent_team.append(TEAM_NAME.get(game.team1, game.team1))
            result.append(game.team2_result)

    context = {
        'user': user,
        'game_data': zip(games, opponent_team, result),
        'win_count': win_count,
        'lose_count': lose_count,
        'stadium_stats': stadium_stats,
        'user_team_fullname': TEAM_NAME.get(user.team, user.team),
    }
    return render(request, 'user_games.html', context)


# 경기장 정보(좌석, 주차, 식당)
def stadium_info(request, stadium):
    ticket_url = request.GET.get('ticket_url', None)
    user = request.user
    stadium_obj = get_object_or_404(Stadium, stadium=stadium)

    seats = Seat.objects.filter(stadium=stadium_obj)
    parkings = Parking.objects.filter(stadium=stadium_obj)
    restaurants = Restaurant.objects.filter(stadium=stadium_obj)

    # 경기장 좌표 및 지도 링크 정보
    team_info = {
        '광주': '35.168275,126.888934,광주기아챔피언스필드,19909618',
        '잠실': '37.512898,127.071107,잠실종합운동장잠실야구장,13202577',
        '문학': '37.435123,126.693024,인천SSG 랜더스필드,13202558',
        '창원': '35.222571,128.582776,NC 다이노스,36046999',
        '대전(신)': '36.317056,127.428072,(구 한화구장)한화생명이글스파크,11831114',
        '고척': '37.498184,126.867129,고척스카이돔,18967604',
        '사직': '35.194956,129.060426,부산사직종합운동장 사직야구장,13202715',
        '대구': '35.841965,128.681198,대구삼성라이온즈파크,19909612',
        '수원': '37.299025,126.974983,수원KT위즈파크,13491582',
        '울산': '35.532168,129.265575,울산문수야구장,1406092164',
        '포항': '36.0081953,129.3593993,포항야구장,11830535'
    }

    lat, lng, name, place_id = team_info[stadium].split(',', 3)

    context = {
        'user': user,
        'stadium': stadium_obj,
        'seats': seats,
        'parkings': parkings,
        'restaurants': restaurants,
        'google_url': f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}&destination_place_id={place_id}",
        'ticket_url': ticket_url,
    }

    return render(request, 'stadium_info.html', context)