import random

def stadium_list(request):
    return {
        'stadiums': [
            '광주', '잠실', '문학', '창원', '대전',
            '고척', '사직', '대구', '수원', '울산', '포항'
        ]
}

def random_changes(request):
    team_icons = [
        'cal/images/mascots/HH.svg',
        'cal/images/mascots/LT.svg',
        'cal/images/mascots/HT.svg',
        'cal/images/mascots/LG.svg',
        'cal/images/mascots/OB.svg',
        'cal/images/mascots/SK.svg',
        'cal/images/mascots/NC.svg',
        'cal/images/mascots/SS.svg',
        'cal/images/mascots/KT.svg',
        'cal/images/mascots/WO.svg',
    ]
    return {
        'random_change': random.choice(team_icons)
    }