import csv
import time
import datetime
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

# KBO 팀 코드 매핑
TEAM_CODE = {
    'LT': 'LT', 'HT': 'HT', 'LG': 'LG', 'OB': 'OB', 'SK': 'SK',
    'WO': 'WO', 'SS': 'SS', 'HH': 'HH', 'KT': 'KT', 'NC': 'NC',
}

# 개별 경기 기록 크롤링 함수
def get_record(date, team1_code, team2_code, game_id, driver):
    url = f'https://m.sports.naver.com/game/{date}{team1_code}{team2_code}{game_id}/record'
    driver.get(url)
    time.sleep(1)

    data = {'away': [], 'home': []}
    columns = ['AB', 'R', 'H', 'RBI', 'HR', 'BB', 'SO', 'SB']

    def extract_pid(th):
        try:
            a = th.find_element(By.TAG_NAME, 'a')
            href = a.get_attribute('href')
            return parse_qs(urlparse(href).query).get('playerId', [''])[0] if href else ''
        except:
            return ''

    try:
        # 어웨이팀 기록
        away_rows = driver.find_elements(By.CSS_SELECTOR, '#content div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child(3) > div > div:nth-child(1) tbody tr')
        for row in away_rows:
            try:
                pid = extract_pid(row.find_element(By.TAG_NAME, 'th'))
                vals = [td.text.strip() for td in row.find_elements(By.TAG_NAME, 'td')]
                if len(vals) >= len(columns):
                    data['away'].append(dict(zip(columns, vals[:len(columns)]), player_id=pid))
            except:
                continue

        # 홈팀 기록
        home_rows = driver.find_elements(By.CSS_SELECTOR, '#content div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child(2) > div > div:nth-child(1) tbody tr')
        for row in home_rows:
            try:
                pid = extract_pid(row.find_element(By.TAG_NAME, 'th'))
                vals = [td.text.strip() for td in row.find_elements(By.TAG_NAME, 'td')]
                if len(vals) >= len(columns):
                    data['home'].append(dict(zip(columns, vals[:len(columns)]), player_id=pid))
            except:
                continue
    except:
        pass

    return data

today = datetime.date.today()

# 기존 파일에서 마지막 저장된 날짜와 game_id 파악
last_date = None
max_game_id = 0

try:
    with open('data/hitters_records.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
        if rows:
            last_date = datetime.datetime.strptime(rows[-1]['date'], '%Y%m%d').date()
            max_game_id = max(int(r['game_id']) for r in rows if r['game_id'].isdigit())
except FileNotFoundError:
    pass

df = pd.read_csv('data/kbo_schedule.csv')
game_map = {}
next_gid = max_game_id + 1

# 기준일자 이전 경기만 필터링 (이미 끝난 경기들만)
df_filtered = df[df['day'].apply(lambda x: datetime.datetime.strptime(x.replace('.', ''), '%Y%m%d').date()) <= today]

# 마지막 기록 이후만 추출
if last_date:
    df_filtered = df_filtered[df_filtered['day'].apply(lambda x: datetime.datetime.strptime(x.replace('.', ''), '%Y%m%d').date()) > last_date]

# 유효한 경기만 game_map에 정리
for _, row in df_filtered.iterrows():
    if str(row.get('canceled', '')).strip() == '취소':
        next_gid += 1
        continue
    if pd.isna(row['team1_score']) or pd.isna(row['team2_score']):
        next_gid += 1
        continue

    d = row['day'].replace('.', '')
    key = (d, row['team1'], row['team2'])
    game_map.setdefault(key, []).append((row, next_gid))
    next_gid += 1

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

# 기록 파일 열기 (없으면 헤더 작성)
with open('data/hitters_records.csv', 'a', newline='', encoding='utf-8-sig') as rout:
    rw = csv.writer(rout)
    if last_date is None:
        rw.writerow(['AB','R','H','RBI','HR','BB','SO','SB','player_id','team','game_id','date'])

    for key, games in game_map.items():
        games_sorted = sorted(games, key=lambda x: x[0]['time'])
        double_header_failed = False

        for idx, (row, gid) in enumerate(games_sorted):
            d, t1, t2 = row['day'].replace('.', ''), row['team1'], row['team2']
            t1c, t2c = TEAM_CODE.get(t1, ''), TEAM_CODE.get(t2, '')
            if not t1c or not t2c:
                continue

            # 네이버 경기 ID 결정 (일반, 더블헤더 1/2차전 등)
            if len(games_sorted) == 1:
                gcode = '02025'
            elif idx == 0:
                gcode = '12025'
            else:
                gcode = '22025' if not double_header_failed else '02025'

            rec = get_record(d, t1c, t2c, gcode, driver)

            # 1차 더블헤더 실패 시, 재시도 여부 판단
            if len(games_sorted) > 1 and idx == 0 and not rec['away'] and not rec['home']:
                double_header_failed = True

            # 2차 더블헤더 실패 시, 일반 코드로 재시도
            if len(games_sorted) > 1 and idx == 1 and not rec['away'] and not rec['home'] and gcode == '22025':
                rec = get_record(d, t1c, t2c, '02025', driver)

            if not rec['away'] and not rec['home']:
                continue

            # 기록 저장
            for team in ['away', 'home']:
                for r in rec[team]:
                    if not r['player_id'].strip():
                        continue
                    rw.writerow([r.get(k, '') for k in ['AB','R','H','RBI','HR','BB','SO','SB']] + [r['player_id'], team, gid, d])

            time.sleep(1.5)

driver.quit()
