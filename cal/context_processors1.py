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
        'cal/images/mascots/HH.webp',
        'cal/images/mascots/LT.webp',
        'cal/images/mascots/HT.webp',
        'cal/images/mascots/LG.webp',
        'cal/images/mascots/OB.webp',
        'cal/images/mascots/SK.webp',
        'cal/images/mascots/NC.webp',
        'cal/images/mascots/SS.webp',
        'cal/images/mascots/KT.webp',
        'cal/images/mascots/WO.webp',
    ]
    return {
        'random_change': random.choice(team_icons)
    }