from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q
from datetime import datetime, timedelta, date
from collections import defaultdict
from .models import *
from accounts.models import User
from .utils import Calendar
import calendar
import random
from collections import defaultdict
import urllib.parse

def calculate_team_standings():
    HOME_STADIUMS = {
        'HT': ['광주'], 'LG': ['잠실'], 'OB': ['잠실'], 'SK': ['문학'],
        'NC': ['창원', '울산'], 'HH': ['대전(신)'], 'WO': ['고척'],
        'LT': ['사직'], 'SS': ['대구', '포항'], 'KT': ['수원'],
    }

    standings = defaultdict(lambda: {
        'W': 0, 'L': 0, 'D': 0,
        'home_W': 0, 'home_L': 0,
        'away_W': 0, 'away_L': 0,
        'weekly_W': 0, 'weekly_L': 0, 'weekly_D': 0,
        'games': []
    })

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    games = Game.objects.exclude(team1_result='').exclude(team2_result='').order_by('date', 'time')

    for game in games:
        t1, t2 = game.team1, game.team2
        r1, r2 = game.team1_result, game.team2_result
        stadium = game.stadium
        date_played = game.date

        # 홈팀 판별 (잠실만 특별 규칙 적용)
        if stadium == '잠실':
            t1_home, t2_home = False, True
        else:
            t1_home = stadium in HOME_STADIUMS.get(t1, [])
            t2_home = stadium in HOME_STADIUMS.get(t2, [])

        # 각 팀 경기 결과 기록
        if r1 in ['승', '패', '무']:
            standings[t1]['games'].append((date_played, r1))
        if r2 in ['승', '패', '무']:
            standings[t2]['games'].append((date_played, r2))

        # 승패 무 기록 업데이트
        if r1 == '승':
            standings[t1]['W'] += 1
            standings[t2]['L'] += 1
            standings[t1]['home_W' if t1_home else 'away_W'] += 1
            standings[t2]['home_L' if t2_home else 'away_L'] += 1
        elif r1 == '패':
            standings[t1]['L'] += 1
            standings[t2]['W'] += 1
            standings[t1]['home_L' if t1_home else 'away_L'] += 1
            standings[t2]['home_W' if t2_home else 'away_W'] += 1
        elif r1 == '무':
            standings[t1]['D'] += 1
            standings[t2]['D'] += 1

        # 주간 기록 업데이트
        if week_start <= date_played <= week_end:
            result_map = {'승': 'weekly_W', '패': 'weekly_L', '무': 'weekly_D'}
            if r1 in result_map:
                standings[t1][result_map[r1]] += 1
            if r2 in result_map:
                standings[t2][result_map[r2]] += 1

    # 최종 팀별 통계 정리
    team_data = []
    for team, record in standings.items():
        total_games = record['W'] + record['L'] + record['D']
        win_percent = round(record['W'] / (record['W'] + record['L']), 3) if (record['W'] + record['L']) > 0 else 0

        recent = [r for _, r in record['games'][-5:]]
        last_10 = [r for _, r in record['games'][-10:]]

        # 연승/연패 계산
        streak = "-"
        if recent:
            current = recent[-1]
            count = 1
            for r in reversed(recent[:-1]):
                if r == current:
                    count += 1
                else:
                    break
            streak = f"{count}{current}"

        team_data.append({
            'team': team,
            'G': total_games,
            'W': record['W'],
            'L': record['L'],
            'D': record['D'],
            'win_percent': win_percent,
            'home': f"{record['home_W']}-{record['home_L']}",
            'away': f"{record['away_W']}-{record['away_L']}",
            'weekly': f"{record['weekly_W']}-{record['weekly_L']}-{record['weekly_D']}",
            'streak': streak,
            'recent_results': recent,
            'games_behind': None,
        })

    # 순위 정렬
    team_data.sort(key=lambda x: x['win_percent'], reverse=True)

    # 게임차 계산
    first = team_data[0]
    for team in team_data:
        if team == first:
            team['games_behind'] = "-"
        else:
            gb = ((first['W'] - team['W']) + (team['L'] - first['L'])) / 2
            team['games_behind'] = round(gb, 1)

    return team_data


# 배경 이미지 랜덤 적용
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
    
    context = {
        'random_bg': random.choice(backgrounds),
        'random_mobile_bg': random.choice(mobile_backgrounds),
        
    }
    return render(request, 'index.html', context)


# 팀 순위 + 유저 팀의 타자/투수 기록 표시
@never_cache
@login_required
def standings(request):
    user_team = request.user.team
    standing = calculate_team_standings()

    hitter_stats = Hitter.objects.filter(team_name=user_team)
    pitcher_stats = Pitcher.objects.filter(team_name=user_team)

    context = {
        'standing': standing,
        'hitter_stats': hitter_stats,
        'pitcher_stats': pitcher_stats,
    }
    return render(request, 'standings.html', context)


# 캘린더 메인 뷰 - 로그인 유저의 팀/출석 데이터 기반
@never_cache
@login_required
def calendar_view(request):
    user = request.user
    user_team = user.team
    attendance_ids = list(user.attendance_game.values_list('id', flat=True))

    current_day = get_date(request.GET.get('day', None))
    calendar = Calendar(current_day.year, current_day.month, team=user_team)
    cal_data = calendar.get_month_data()

    standing = calculate_team_standings()

    context = {
        'cal_data': cal_data,
        'prev_month': prev_month(current_day),
        'next_month': next_month(current_day),
        'user_team': user_team,
        'user_attendance_game_ids': attendance_ids,
        'standing': standing,
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

    # 👉 유저 팀 정보
    user_team = request.user.team

    # 👉 우리 팀 소속 타자 ID들
    our_hitter_ids = set(Hitter.objects.filter(team_name=user_team).values_list('player_id', flat=True))

    # 👉 우리 팀 소속 투수 ID들
    our_pitcher_ids = set(Pitcher.objects.filter(team_name=user_team).values_list('player_id', flat=True))

    # 👉 오늘 경기 중 우리 팀 타자 기록만
    today_hitters = [r for r in today_hitter_records if r.player_id in our_hitter_ids]

    # 👉 오늘 경기 중 우리 팀 투수 기록만
    today_pitchers = [r for r in today_pitcher_records if r.player_id in our_pitcher_ids]

    # 👉 오늘 기록이 없으면, 최신 기록 중 우리 팀만
    if not today_hitters:
        team_hitters = [r for r in latest_daily_stats.values() if r.player_id in our_hitter_ids]
        best_hitter = max(team_hitters, key=calculate_hitter_score, default=None)
    else:
        best_hitter = max(today_hitters, key=calculate_hitter_score, default=None)

    if not today_pitchers:
        team_pitchers = [r for r in latest_pitcher_stats.values() if r.player_id in our_pitcher_ids]
        best_pitcher = max(team_pitchers, key=calculate_pitcher_score, default=None)
    else:
        best_pitcher = max(today_pitchers, key=calculate_pitcher_score, default=None)


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
        best_player = None
        best_player_name = "-"
        player_type = "-"
        score = 0
    
    is_today_best = best_player and best_player.date == game.date

    # 라인업 분기
    if has_lineup:
        pitcher_indexes = [i for i, l in enumerate(lineups) if l.batting_order == 1]
        if len(pitcher_indexes) >= 2:
            away_lineup = lineups[pitcher_indexes[0]:pitcher_indexes[0]+10]
            home_lineup = lineups[pitcher_indexes[1]:pitcher_indexes[1]+10]

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
        opponent_team = game.team2 if user_team == game.team1 else game.team1

    # 점수 처리
    if request.user.team == game.team1:
        user_score = game.team1_score
        opponent_score = game.team2_score
    else:
        user_score = game.team2_score
        opponent_score = game.team1_score

    # 경기 종료 여부
    is_after_game = (game.team1_score is not None) and (game.team2_score is not None)
    show_best_player = is_after_game and (user_score > opponent_score)

    # 티켓링크 처리
    stadium_ticket = game.stadium

    ticket = {
        "대전(신)": "https://www.ticketlink.co.kr/sports/137/63",
        "수원": "https://www.ticketlink.co.kr/sports/137/62",
        "광주": "https://www.ticketlink.co.kr/sports/137/58",
        "대구": "https://www.ticketlink.co.kr/sports/137/57",
        '포항': "https://www.ticketlink.co.kr/sports/137/57",
        "문학": "https://www.ticketlink.co.kr/sports/137/476",
        "고척": "https://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode=07001&TeamCode=PB003",
        "사직": "https://ticket.giantsclub.com/loginForm.do",
        "창원": "https://ticket.ncdinos.com/games",
        '울산': "https://ticket.ncdinos.com/games",
    }

    # 이전/다음 경기 버튼
    team_games = Game.objects.filter(
        Q(team1=user_team) | Q(team2=user_team)
    ).exclude(
        team1_result="취소"
    ).exclude(
        team2_result="취소"
    ).order_by('date', 'id')

    team_game_ids = list(team_games.values_list('id', flat=True))

    try:
        current_index = team_game_ids.index(game.id)
        prev_game_id = team_game_ids[current_index - 1] if current_index > 0 else None
        next_game_id = team_game_ids[current_index + 1] if current_index < len(team_game_ids) - 1 else None
    except ValueError:
        prev_game_id = None
        next_game_id = None


    context = {
        'game': game,
        'user_lineup': user_lineup,
        'opponent_lineup': opponent_lineup,
        'user_team': user_team,
        'opponent_team': opponent_team,
        'has_lineup': has_lineup,
        'latest_daily_stats': latest_daily_stats,
        'latest_pitcher_stats': latest_pitcher_stats,
        'today': game.date,
        'user_score': user_score,
        'opponent_score': opponent_score,
        'is_after_game': is_after_game,
        'ticket_url': ticket.get(stadium_ticket, "#"),
        'best_player': best_player,
        'best_player_name': best_player_name,
        'player_type': player_type,
        'score': round(score, 2),
        'is_today_best': is_today_best,
        'show_best_player': show_best_player,
        'prev_game_id': prev_game_id,
        'next_game_id': next_game_id,
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
    user = request.user
    stadium_obj = get_object_or_404(Stadium, stadium=stadium)

    seats = Seat.objects.filter(stadium=stadium_obj)
    parkings = Parking.objects.filter(stadium=stadium_obj)
    restaurants = Restaurant.objects.filter(stadium=stadium_obj)

    # 경기장 좌표 및 지도 링크 정보
    team_info = {
        '광주': '35.168275,126.888934,광주기아챔피언스필드,19909618',
        '잠실': '37.512898,127.071107,잠실종합운동장 잠실야구장,13202577',
        '문학': '37.435123,126.693024,인천SSG 랜더스필드,13202558',
        '창원': '35.222571,128.582776,NC 다이노스,36046999',
        '대전(신)': '36.317056,127.428072, 한화생명이글스파크,11831114',
        '고척': '37.498184,126.867129,고척스카이돔,18967604',
        '사직': '35.194956,129.060426,부산사직종합운동장 사직야구장,13202715',
        '대구': '35.841965,128.681198,대구삼성라이온즈파크,19909612',
        '수원': '37.299025,126.974983,수원KT위즈파크,13491582',
        '울산': '35.532168,129.265575,울산문수야구장,1406092164',
        '포항': '36.0081953,129.3593993,포항야구장,11830535'
    }

    lat, lng, name, place_id = team_info[stadium].split(',', 3)
    encoded_name = urllib.parse.quote(name)

    naver_url =f"nmap://route/public?dlat={lat}&dlng={lng}&dname={encoded_name}"

    # 티켓링크 처리
    stadium_ticket = stadium

    ticket = {
        "대전(신)": "https://www.ticketlink.co.kr/sports/137/63",
        "수원": "https://www.ticketlink.co.kr/sports/137/62",
        "광주": "https://www.ticketlink.co.kr/sports/137/58",
        "대구": "https://www.ticketlink.co.kr/sports/137/57",
        '포항': "https://www.ticketlink.co.kr/sports/137/57",
        "문학": "https://www.ticketlink.co.kr/sports/137/476",
        "고척": "https://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode=07001&TeamCode=PB003",
        "사직": "https://ticket.giantsclub.com/loginForm.do",
        "창원": "https://ticket.ncdinos.com/games",
        '울산': "https://ticket.ncdinos.com/games",
    }

    context = {
        'user': user,
        'stadium': stadium_obj,
        'seats': seats,
        'parkings': parkings,
        'restaurants': restaurants,
        'google_url': f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}&destination_place_id={place_id}",
        'naver_url': naver_url,
        'ticket_url': ticket.get(stadium_ticket, "#"),
    }

    return render(request, 'stadium_info.html', context)