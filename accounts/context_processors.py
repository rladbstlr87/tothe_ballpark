def win_count_total(request):
    win_count = 0
    user_team = None
    if request.user.is_authenticated:
        user_team = request.user.team
        for game in request.user.attendance_game.all():
            game_result = game.team1_result if game.team1 == user_team else game.team2_result
            if game_result == '승':
                win_count += 1
    total_games = request.user.attendance_game.count()
    if total_games == 0:
        winnning_percent = 0
    else:
        winnning_percent = (win_count / total_games) * 100
    return {'winning_percent': winnning_percent}