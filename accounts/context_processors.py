from django.contrib.auth import get_user_model

def win_count_total(request):
    if not request.user.is_authenticated:
        return {}

    win_count = 0
    user_team = request.user.team
    for game in request.user.attendance_game.all():
        game_result = game.team1_result if game.team1 == user_team else game.team2_result
        if game_result == '승':
            win_count += 1

    total_games = request.user.attendance_game.count()
    if total_games == 0:
        winning_percent = 0
    else:
        winning_percent = (win_count / total_games) * 100

    return {'winning_percent': winning_percent}

def all_users_winning_percent(request):
    if not request.user.is_authenticated:
        return {}

    User = get_user_model()
    all_users = User.objects.all()
    user_win_data = []
    for user in all_users:
        games = user.attendance_game.all()
        total_games = games.count()
        win_count = 0
        for game in games:
            user_team = user.team
            game_result = game.team1_result if game.team1 == user_team else game.team2_result
            if game_result == '승':
                win_count += 1
        winning_percent = round((win_count / total_games) * 100, 2) if total_games > 0 else 0
        user_win_data.append({
            'username': user.username,
            'nickname': user.nickname,
            'winning_percent': winning_percent,
            'total_games': total_games,
            'win_count': win_count
        })

    # 승률 기준으로 내림차순 정렬
    user_win_data.sort(key=lambda x: x['winning_percent'], reverse=True)

    return {'all_users_winning_percent': user_win_data}