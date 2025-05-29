def win_count_total(request):
    if not request.user.is_authenticated:
        return {}  # 비로그인 상태에서는 아무것도 반환하지 않음

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