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
    parts = ip_str.split()
    if len(parts) == 1:
        try:
            return float(parts[0])
        except ValueError:
            return 0.0
    elif len(parts) == 2:
        whole = float(parts[0])
        fraction_map = {'⅓': 1/3, '⅔': 2/3}
        fraction = fraction_map.get(parts[1], 0)
        return round(whole + fraction, 3)
    return 0.0

# 투수 기록 크롤링
def get_pitcher_record(date, team1_code, team2_code, game_id, driver):
    url = f'https://m.sports.naver.com/game/{date}{team1_code}{team2_code}{game_id}/record'
    driver.get(url)
    time.sleep(1)

    data = {'away': None, 'home': None}
    columns = ['IP', 'H', 'R', 'ER', 'BB', 'SO', 'HR', 'BF', 'AB', 'NP']

    try:
        away_th = driver.find_element(By.CSS_SELECTOR,
            '#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child(7) > table > tbody > tr:nth-child(1) > th')
        away_td = driver.find_elements(By.CSS_SELECTOR,
            '#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child(7) > table > tbody > tr:nth-child(1) > td')
        data['away'] = {'player_id': extract_pid(away_th)}
        for key, td in zip(columns, away_td):
            data['away'][key] = td.text.strip()

        home_th = driver.find_element(By.CSS_SELECTOR,
            '#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child(8) > table > tbody > tr:nth-child(1) > th')
        home_td = driver.find_elements(By.CSS_SELECTOR,
            '#content > div > div.Home_main_section__y9jR4 > section.Home_game_panel__97L_8 > div.Home_game_contents__35IMT > div > div.PlayerRecord_comp_player_record__1tI5G.type_kbo > div:nth-child(8) > table > tbody > tr:nth-child(1) > td')
        data['home'] = {'player_id': extract_pid(home_th)}
        for key, td in zip(columns, home_td):
            data['home'][key] = td.text.strip()
    except Exception as e:
        print("⚠️ 투수 기록 추출 실패:", e)

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
                if rec[team]:
                    r = rec[team]
                    pw.writerow([
                        convert_ip_to_float(r.get('IP', '')),
                        r.get('H', ''), r.get('R', ''), r.get('ER', ''), r.get('BB', ''),
                        r.get('SO', ''), r.get('HR', ''), r.get('BF', ''), r.get('AB', ''),
                        r.get('NP', ''), r['player_id'], team, gid, d
                    ])

            print(f"✅ 저장 완료: {d} {t1} vs {t2} ({gcode}) → game_id={gid}")
            time.sleep(1.5)

print('✅ 모든 투수 기록 저장 완료')
driver.quit()
