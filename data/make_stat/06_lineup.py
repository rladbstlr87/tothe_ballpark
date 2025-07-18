import time
import datetime
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import sys
import django

# Django 환경 설정
sys.path.append('/Users/m2/Desktop/tothe_ballpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baseball.settings')
django.setup()

from cal.models import Game, Lineup, Hitter, Pitcher, Stadium

# --- KBO 팀 코드 매핑 ---
TEAM_CODE = {
    'LT': 'LT', 'HT': 'HT', 'LG': 'LG', 'OB': 'OB', 'SK': 'SK',
    'WO': 'WO', 'SS': 'SS', 'HH': 'HH', 'KT': 'KT', 'NC': 'NC',
}

# --- 라인업 스크래핑 함수 ---
def get_lineup(today, team1_code, team2_code, game_id, driver):
    url = f'https://m.sports.naver.com/game/{today}{team1_code}{team2_code}{game_id}/lineup'
    driver.get(url)
    time.sleep(1.5)
    try:
        lineup_boxes = driver.find_elements(By.CSS_SELECTOR, 'div.Lineup_comp_lineup__361i1 > div > div')
        team1, team2 = [], []
        for idx, team_box in enumerate(lineup_boxes[:2]):
            players = team_box.find_elements(By.CSS_SELECTOR, 'ol > li > a')
            player_info = []
            for player in players:
                name = player.find_element(By.CSS_SELECTOR, 'div > strong').text.strip()
                href = player.get_attribute('href')
                player_id = ''.join(filter(str.isdigit, href.split('playerId=')[-1])) if href else ''
                player_info.append((name, player_id))
            if idx == 0: team1 = player_info
            else: team2 = player_info
        return team1, team2
    except Exception: return [], []

# --- 스크래핑 설정 ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# --- 오늘 날짜 및 경기 정보 가져오기 ---
today = datetime.date.today()
games_today = Game.objects.filter(date=today)

# --- 라인업 정보 처리 및 DB 저장 ---
for game in games_today:
    date_str = game.date.strftime('%Y%m%d')
    team1_code = game.team1
    team2_code = game.team2

    # 네이버 경기 ID 결정 (현재는 일반 경기만 가정)
    naver_game_id = '0' # 일반 경기

    team1_lineup, team2_lineup = get_lineup(date_str, team1_code, team2_code, naver_game_id, driver)

    # Stadium 객체 가져오기
    stadium_obj, _ = Stadium.objects.get_or_create(stadium=game.stadium)

    # 라인업 정보 저장
    for i, (player_name, player_id) in enumerate(team1_lineup):
        if not player_id: continue
        is_pitcher = i == 0
        batting_order = None if is_pitcher else i

        lineup_data = {
            'game': game,
            'stadium': stadium_obj,
            'batting_order': batting_order
        }

        if is_pitcher:
            pitcher_obj, _ = Pitcher.objects.get_or_create(player_id=player_id, defaults={'player_name': player_name, 'team_name': team1_code})
            lineup_data['pitcher'] = pitcher_obj
        else:
            hitter_obj, _ = Hitter.objects.get_or_create(player_id=player_id, defaults={'player_name': player_name, 'team_name': team1_code})
            lineup_data['hitter'] = hitter_obj
        
        Lineup.objects.update_or_create(game=game, player_id=player_id, defaults=lineup_data)


    for i, (player_name, player_id) in enumerate(team2_lineup):
        if not player_id: continue
        is_pitcher = i == 0
        batting_order = None if is_pitcher else i

        lineup_data = {
            'game': game,
            'stadium': stadium_obj,
            'batting_order': batting_order
        }

        if is_pitcher:
            pitcher_obj, _ = Pitcher.objects.get_or_create(player_id=player_id, defaults={'player_name': player_name, 'team_name': team2_code})
            lineup_data['pitcher'] = pitcher_obj
        else:
            hitter_obj, _ = Hitter.objects.get_or_create(player_id=player_id, defaults={'player_name': player_name, 'team_name': team2_code})
            lineup_data['hitter'] = hitter_obj

        Lineup.objects.update_or_create(game=game, player_id=player_id, defaults=lineup_data)

driver.quit()
print("Lineup data updated successfully.")