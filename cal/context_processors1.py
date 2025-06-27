import random

def stadium_list(request):
    return {
        'stadiums': [
            '광주', '잠실', '문학', '창원', '대전(신)',
            '고척', '사직', '대구', '수원', '울산', '포항'
        ]
}
def random_backgrounds(request):
    team_icons = [
        'cal/images/mascots/HHline.svg',
        'cal/images/mascots/LTline.svg',
        'cal/images/mascots/HTline.svg',
        'cal/images/mascots/LGline.svg',
        'cal/images/mascots/OBline.svg',
        'cal/images/mascots/SKline.svg',
        'cal/images/mascots/NCline.svg',
        'cal/images/mascots/SSline.svg',
        'cal/images/mascots/KTline.svg',
        'cal/images/mascots/WOline.svg',
    ]
    return {
        'random_background': random.choice(team_icons)
    }