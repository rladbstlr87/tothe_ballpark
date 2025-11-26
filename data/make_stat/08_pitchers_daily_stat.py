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


def resolve_year_code(date_str: str) -> str:
    """
    2025 포스트시즌(10/6 이후) 연도 코드 보정:
    WC/준PO/PO/KS => 4444/3333/5555/7777
    """
    base_year = date_str[:4] if len(date_str) >= 4 else "2025"
    if base_year != "2025":
        return base_year
    try:
        date_int = int(date_str)
    except ValueError:
        return base_year

    if date_int >= 20251026:
        return "7777"
    if date_int >= 20251017:
        return "5555"
    if date_int >= 20251009:
        return "3333"
    if date_int >= 20251006:
        return "4444"
    return base_year

today = datetime.date.today()

# 기존 파일에서 마지막 저장된 날짜와 game_id 파악
last_date = None
max_game_id = 0

def _safe_date(s: str):
    try:
        return datetime.datetime.strptime(s, '%Y%m%d').date()
    except Exception:
        return None

try:
    with open('data/pitchers_records.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
        for r in reversed(rows):
            d = _safe_date(r.get('date', ''))
            if d:
                last_date = d
                break
        ids = [int(r['game_id']) for r in rows if str(r.get('game_id', '')).isdigit()]
        if ids:
            max_game_id = max(ids)
except FileNotFoundError:
    pass

df = pd.read_csv('data/kbo_schedule.csv')
game_map = {}
next_gid = max_game_id + 1
base_start_date = datetime.date(2025, 10, 6)
start_date = max(base_start_date, last_date + datetime.timedelta(days=1)) if last_date else base_start_date

# 기준일자 이전 경기만 필터링 (이미 끝난 경기들만)
df = df.assign(day_date=df['day'].apply(lambda x: datetime.datetime.strptime(x.replace('.', ''), '%Y%m%d').date()))
df_filtered = df[(df['day_date'] >= start_date) & (df['day_date'] <= today)]

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
            year_code = resolve_year_code(d)
            url_date = f"{year_code}{d[4:]}" if len(d) == 8 and year_code != d[:4] else d

            # 네이버 경기 ID 결정 (일반, 더블헤더 1/2차전 등)
            single_game_id = f'0{year_code}'
            first_game_id = f'1{year_code}'
            second_game_id = f'2{year_code}'

            if len(games_sorted) == 1:
                gcode = single_game_id
            elif idx == 0:
                gcode = first_game_id
            else:
                gcode = second_game_id if not double_header_failed else single_game_id

            attempts = []
            attempts.append((url_date, gcode))
            if url_date != d:
                attempts.append((d, gcode))
            base_id = f"{gcode[0]}{d[:4]}"
            if base_id != gcode:
                attempts.append((url_date, base_id))
                if url_date != d:
                    attempts.append((d, base_id))

            rec = {'away': [], 'home': []}
            for dt_for_url, gid_str in attempts:
                rec = get_pitcher_record(dt_for_url, t1c, t2c, gid_str)
                if rec.get('away') or rec.get('home'):
                    break

            # 1차 더블헤더 실패 시, 재시도 여부 판단
            if len(games_sorted) > 1 and idx == 0 and not rec['away'] and not rec['home']:
                double_header_failed = True

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
