import csv
import time
import datetime
from stat_def import TEAM_NAVER
import json
import urllib.request
import pandas as pd


# 개별 경기 기록 크롤링 함수
def get_record(date, team1_code, team2_code, game_id):
    api_url = f"https://api-gw.sports.naver.com/schedule/games/{date}{team1_code}{team2_code}{game_id}/record"
    data = {"away": [], "home": []}
    columns = ["AB", "R", "H", "RBI", "HR", "BB", "SO", "SB"]

    try:
        res = urllib.request.urlopen(api_url, timeout=8)
        obj = json.loads(res.read())
        record = obj.get("result", {}).get("recordData", {})
        batters = record.get("battersBoxscore", {})
        for side in ["away", "home"]:
            rows = batters.get(side, [])
            for r in rows:
                pid = str(r.get("playerCode", "")).strip()
                vals = [
                    r.get("ab", ""),
                    r.get("run", ""),
                    r.get("hit", ""),
                    r.get("rbi", ""),
                    r.get("hr", ""),
                    r.get("bb", ""),
                    r.get("kk", ""),
                    r.get("sb", ""),
                ]
                data[side].append(dict(zip(columns, vals), player_id=pid))
    except Exception as e:
        pass

    return data

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
    with open('data/hitters_records.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
        # 마지막 유효 날짜만 선택 (헤더 중복 등 방지)
        for r in reversed(rows):
            d = _safe_date(r.get('date', ''))
            if d:
                last_date = d
                break
        # 유효한 game_id만 계산
        ids = [int(r['game_id']) for r in rows if str(r.get('game_id', '')).isdigit()]
        if ids:
            max_game_id = max(ids)
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
with open('data/hitters_records.csv', 'a', newline='', encoding='utf-8-sig') as rout:
    rw = csv.writer(rout)
    if last_date is None:
        rw.writerow(['AB','R','H','RBI','HR','BB','SO','SB','player_id','team','game_id','date'])

    valid_pids = set(pd.read_csv('data/all_hitter_stats.csv', dtype={'player_id': str})['player_id'].astype(str))
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

            rec = get_record(d, t1c, t2c, gcode)

            # 1차 더블헤더 실패 시, 재시도 여부 판단
            if len(games_sorted) > 1 and idx == 0 and not rec['away'] and not rec['home']:
                double_header_failed = True

            # 2차 더블헤더 실패 시, 일반 코드로 재시도
            if len(games_sorted) > 1 and idx == 1 and not rec['away'] and not rec['home'] and gcode == '22025':
                rec = get_record(d, t1c, t2c, '02025')

            if not rec['away'] and not rec['home']:
                continue

            # 기록 저장
            for team in ['away', 'home']:
                for r in rec[team]:
                    pid = r.get('player_id')
                    if not pid or pid not in valid_pids:
                        continue
                    rw.writerow([r.get(k, '') for k in ['AB','R','H','RBI','HR','BB','SO','SB']] + [pid, team, gid, d])

            time.sleep(1.5)
