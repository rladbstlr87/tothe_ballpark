import csv
import time
import datetime
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

TEAM_CODE = {
    'LT': 'LT', 'HT': 'HT', 'LG': 'LG', 'OB': 'OB', 'SK': 'SK',
    'WO': 'WO', 'SS': 'SS', 'HH': 'HH', 'KT': 'KT', 'NC': 'NC',
}

# player_id 추출
def extract_pid(th):
    try:
        a = th.find_element(By.TAG_NAME, 'a')
        href = a.get_attribute('href')
        return parse_qs(urlparse(href).query).get('playerId', [''])[0] if href else ''
    except:
        return ''

# IP (이닝) 문자열을 실수로 변환
def convert_ip_to_float(ip_str):
    if not ip_str:
        return 0.0
    ip_str = ip_str.strip()
    
    fraction_map = {'⅓': 1/3, '⅔': 2/3}
    
    if ip_str in fraction_map:
        return round(fraction_map[ip_str], 3)
    
    parts = ip_str.split()
    if len(parts) == 1:
        try:
            return float(parts[0])
        except ValueError:
            return 0.0
    elif len(parts) == 2:
        try:
            whole = float(parts[0])
            fraction = fraction_map.get(parts[1], 0)
            return round(whole + fraction, 3)
        except ValueError:
            return 0.0
    return 0.0

# 투수 기록 크롤링
def get_pitcher_record(date, team1_code, team2_code, game_id, driver):
    url = f'https://m.sports.naver.com/game/{date}{team1_code}{team2_code}{game_id}/record'
    driver.get(url)
    time.sleep(1)

    data = {'away': [], 'home': []}
    columns = ['IP', 'H', 'R', 'ER', 'BB', 'SO', 'HR', 'BF', 'AB', 'NP']

    try:
        # 어웨이팀 기록
        away_rows = driver.find_elements(By.CSS_SELECTOR, '#content div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child(3) > div > div:nth-child(2) tbody tr')
        for row in away_rows:
            try:
                pid = extract_pid(row.find_element(By.TAG_NAME, 'th'))
                vals = [td.text.strip() for td in row.find_elements(By.TAG_NAME, 'td')]
                if len(vals) >= len(columns):
                    data['away'].append(dict(zip(columns, vals[:len(columns)]), player_id=pid))
            except:
                continue

        # 홈팀 기록
        home_rows = driver.find_elements(By.CSS_SELECTOR, '#content div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child(2) > div > div:nth-child(2) tbody tr')
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

# 날짜/게임 ID 초기화
today = datetime.date.today()
last_date = None
max_game_id = 0

try:
    with open('../pitchers_records.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
        if rows:
            last_date = datetime.datetime.strptime(rows[-1]['date'], '%Y%m%d').date()
            max_game_id = max(int(r['game_id']) for r in rows if r['game_id'].isdigit())
except FileNotFoundError:
    pass

df = pd.read_csv('../kbo_schedule.csv')
game_map = {}
next_gid = max_game_id + 1

df_filtered = df[df['day'].apply(lambda x: datetime.datetime.strptime(x.replace('.', ''), '%Y%m%d').date()) <= today]
if last_date:
    df_filtered = df_filtered[df_filtered['day'].apply(lambda x: datetime.datetime.strptime(x.replace('.', ''), '%Y%m%d').date()) > last_date]

for _, row in df_filtered.iterrows():
    if str(row.get('canceled', '')).strip() == '취소':
        print(f"⛔ 취소된 경기: {row['day']} {row['team1']} vs {row['team2']} ({row['time']})")
        next_gid += 1
        continue
    if pd.isna(row['team1_score']) or pd.isna(row['team2_score']):
        print(f"⛔ 점수 없음: {row['day']} {row['team1']} vs {row['team2']} ({row['time']})")
        next_gid += 1
        continue

    d = row['day'].replace('.', '')
    key = (d, row['team1'], row['team2'])
    game_map.setdefault(key, []).append((row, next_gid))
    next_gid += 1

# 크롬 드라이버 실행
driver = webdriver.Chrome()
driver.fullscreen_window()

with open('../pitchers_records.csv', 'a', newline='', encoding='utf-8-sig') as prout:
    pw = csv.writer(prout)

    if last_date is None:
        pw.writerow(['IP','H','R','ER','BB','SO','HR','BF','AB','NP','player_id','team','game_id','date'])

    for key, games in game_map.items():
        games_sorted = sorted(games, key=lambda x: x[0]['time'])
        double_header_failed = False

        for idx, (row, gid) in enumerate(games_sorted):
            d, t1, t2 = row['day'].replace('.', ''), row['team1'], row['team2']
            t1c, t2c = TEAM_CODE.get(t1, ''), TEAM_CODE.get(t2, '')
            if not t1c or not t2c:
                print(f"⚠️ 팀 코드 누락: {t1}, {t2}")
                continue

            if len(games_sorted) == 1:
                gcode = '02025'
            elif idx == 0:
                gcode = '12025'
            else:
                gcode = '22025' if not double_header_failed else '02025'

            rec = get_pitcher_record(d, t1c, t2c, gcode, driver)

            if len(games_sorted) > 1 and idx == 0 and not rec['away'] and not rec['home']:
                double_header_failed = True

            if len(games_sorted) > 1 and idx == 1 and not rec['away'] and not rec['home'] and gcode == '22025':
                print(f"🔁 {d} {t1} vs {t2} 2차 기록 없음, 02025로 재시도")
                rec = get_pitcher_record(d, t1c, t2c, '02025', driver)

            if not rec['away'] and not rec['home']:
                print(f"⚠️ 투수 기록 없음: {d} {t1} vs {t2} ({gcode})")
                continue

            for team in ['away', 'home']:
                for r in rec[team]:
                    pid = r.get('player_id', '').strip()
                    if not pid:  # 공백이거나 None이면 저장하지 않음
                        continue
                    pw.writerow([
                        convert_ip_to_float(r.get('IP', '')),
                        r.get('H', ''), r.get('R', ''), r.get('ER', ''), r.get('BB', ''),
                        r.get('SO', ''), r.get('HR', ''), r.get('BF', ''), r.get('AB', ''),
                        r.get('NP', ''), pid, team, gid, d
                    ])

            print(f"✅ 저장 완료: {d} {t1} vs {t2} ({gcode}) → game_id={gid}")
            time.sleep(1.5)

print('✅ 모든 투수 기록 저장 완료')
driver.quit()
