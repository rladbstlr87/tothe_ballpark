import csv
import time
import datetime
from stat_def import TEAM_NAVER
import json
import urllib.request
import pandas as pd


# IP 문자열을 실수로 변환
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

def get_pitcher_record(date, team1_code, team2_code, game_id):
    api_url = f"https://api-gw.sports.naver.com/schedule/games/{date}{team1_code}{team2_code}{game_id}/record"
    data = {'away': [], 'home': []}
    columns = ['IP', 'H', 'R', 'ER', 'BB', 'SO', 'HR', 'BF', 'AB', 'NP']

    try:
        res = urllib.request.urlopen(api_url, timeout=8)
        obj = json.loads(res.read())
        record = obj.get('result', {}).get('recordData', {})
        pitchers = record.get('pitchersBoxscore', {})
        for side in ['away', 'home']:
            rows = pitchers.get(side, [])
            for r in rows:
                pid = str(r.get('pcode', '')).strip()
                # API가 소수 이닝을 문자열로 주므로 그대로 사용 후 convert_ip_to_float에서 변환
                vals = [
                    r.get('inn', ''),
                    r.get('hit', ''),
                    r.get('r', ''),
                    r.get('er', ''),
                    r.get('bb', ''),
                    r.get('kk', ''),
                    r.get('hr', ''),
                    r.get('bf', ''),
                    r.get('ab', ''),
                    r.get('np', ''),  # 투구수 np가 없을 수 있음
                ]
                data[side].append(dict(zip(columns, vals), player_id=pid))
    except Exception:
        pass

    return data

today = datetime.date.today()

# 기존 파일에서 마지막 저장된 날짜와 game_id 파악
last_date = None
max_game_id = 0

try:
    with open('data/pitchers_records.csv', 'r', encoding='utf-8-sig') as f:
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

# 기록 파일 열기 (없으면 헤더 작성)
with open('data/pitchers_records.csv', 'a', newline='', encoding='utf-8-sig') as prout:
    pw = csv.writer(prout)

    if last_date is None:
        pw.writerow(['IP','H','R','ER','BB','SO','HR','BF','AB','NP','player_id','team','game_id','date'])

    for key, games in game_map.items():
        games_sorted = sorted(games, key=lambda x: x[0]['time'])
        double_header_failed = False

        for idx, (row, gid) in enumerate(games_sorted):
            d, t1, t2 = row['day'].replace('.', ''), row['team1'], row['team2']
            t1c, t2c = TEAM_NAVER.get(t1, ''), TEAM_NAVER.get(t2, '')
            if not t1c or not t2c:
                continue

            # 네이버 경기 ID 결정 (일반, 더블헤더 1/2차전 등)
            if len(games_sorted) == 1:
                gcode = '02025'
            elif idx == 0:
                gcode = '12025'
            else:
                gcode = '22025' if not double_header_failed else '02025'

            rec = get_pitcher_record(d, t1c, t2c, gcode)

            # 1차 더블헤더 실패 시, 재시도 여부 판단
            if len(games_sorted) > 1 and idx == 0 and not rec['away'] and not rec['home']:
                double_header_failed = True

            # 2차 더블헤더 실패 시, 일반 코드로 재시도
            if len(games_sorted) > 1 and idx == 1 and not rec['away'] and not rec['home'] and gcode == '22025':
                rec = get_pitcher_record(d, t1c, t2c, '02025')

            if not rec['away'] and not rec['home']:
                continue

            # 기록 저장
            for team in ['away', 'home']:
                for r in rec[team]:
                    pid = r.get('player_id', '').strip()
                    if not pid:
                        continue
                    pw.writerow([
                        convert_ip_to_float(r.get('IP', '')),
                        r.get('H', ''), r.get('R', ''), r.get('ER', ''), r.get('BB', ''),
                        r.get('SO', ''), r.get('HR', ''), r.get('BF', ''), r.get('AB', ''),
                        r.get('NP', ''), pid, team, gid, d
                    ])

            time.sleep(1.5)
