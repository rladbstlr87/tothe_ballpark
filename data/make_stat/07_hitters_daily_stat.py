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

from cal.models import Game, Hitter, Hitter_Daily

# --- KBO 팀 코드 매핑 ---
TEAM_CODE = {
    'LT': 'LT', 'HT': 'HT', 'LG': 'LG', 'OB': 'OB', 'SK': 'SK',
    'WO': 'WO', 'SS': 'SS', 'HH': 'HH', 'KT': 'KT', 'NC': 'NC',
}

# --- 기록 스크래핑 함수 ---
def get_record(date, team1_code, team2_code, game_id, driver):
    url = f'https://m.sports.naver.com/game/{date}{team1_code}{team2_code}{game_id}/record'
    driver.get(url)
    time.sleep(1.5)
    data = {'away': [], 'home': []}
    columns = ['AB', 'R', 'H', 'RBI', 'HR', 'BB', 'SO', 'SB']

    def extract_pid(th):
        try:
            a = th.find_element(By.TAG_NAME, 'a')
            href = a.get_attribute('href')
            return parse_qs(urlparse(href).query).get('playerId', [''])[0] if href else ''
        except: return ''

    try:
        for team_type, child_num in [('away', 3), ('home', 2)]:
            rows = driver.find_elements(By.CSS_SELECTOR, f'#content div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child({child_num}) > div > div:nth-child(1) tbody tr')
            for row in rows:
                try:
                    pid = extract_pid(row.find_element(By.TAG_NAME, 'th'))
                    if not pid: continue
                    vals = [td.text.strip() for td in row.find_elements(By.TAG_NAME, 'td')]
                    if len(vals) >= len(columns):
                        data[team_type].append(dict(zip(columns, vals[:len(columns)]), player_id=pid))
                except: continue
    except: pass
    return data

# --- 스크래핑 설정 ---
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

# --- 어제 날짜 및 경기 정보 가져오기 ---
yesterday = datetime.date.today() - datetime.timedelta(days=1)
games_yesterday = Game.objects.filter(date=yesterday, team1_score__isnull=False, team2_score__isnull=False).exclude(note__contains='취소')

# --- 기록 처리 및 DB 저장 ---
for game in games_yesterday:
    date_str = game.date.strftime('%Y%m%d')
    t1c, t2c = game.team1, game.team2
    
    # 네이버 경기 ID (일반 경기만 가정)
    gcode = '0'

    rec = get_record(date_str, t1c, t2c, gcode, driver)
    if not rec['away'] and not rec['home']: continue

    for team_type, team_code in [('away', t1c), ('home', t2c)]:
        for r in rec[team_type]:
            player_id = r.get('player_id')
            if not player_id: continue

            try:
                player_obj = Hitter.objects.get(player_id=player_id)
            except Hitter.DoesNotExist:
                continue

            daily_data = {
                'game_id': game,
                'date': game.date,
                'player': player_obj,
                'team': team_code,
                'AB': int(r.get('AB', 0)), 'R': int(r.get('R', 0)), 'H': int(r.get('H', 0)),
                'RBI': int(r.get('RBI', 0)), 'HR': int(r.get('HR', 0)), 'BB': int(r.get('BB', 0)),
                'SO': int(r.get('SO', 0)), 'SB': int(r.get('SB', 0)),
            }
            Hitter_Daily.objects.update_or_create(
                game_id=game, player=player_obj, defaults=daily_data
            )
    time.sleep(1.5)

driver.quit()
print("Hitter daily stats updated successfully.")