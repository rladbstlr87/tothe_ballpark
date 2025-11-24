import csv
import time
import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# KBO 팀 코드 매핑
TEAM_CODE = {
    'LT': 'LT', 'HT': 'HT', 'LG': 'LG', 'OB': 'OB', 'SK': 'SK',
    'WO': 'WO', 'SS': 'SS', 'HH': 'HH', 'KT': 'KT', 'NC': 'NC',
}

def debug(msg):
    print(f"[lineup-debug] {msg}", flush=True)

# 특정 경기의 라인업 페이지에서 선수 이름과 playerId를 가져오는 함수
def get_lineup(today, team1_code, team2_code, game_id, driver):
    url = f"https://m.sports.naver.com/game/{today}{team1_code}{team2_code}{game_id}/lineup"
    driver.get(url)

    # 1) 라인업의 선수 a/img가 로드될 때까지 대기 (최대 8초)
    try:
        WebDriverWait(driver, 8).until(
            lambda d: d.execute_script(
                'return document.querySelectorAll("div.Lineup_comp_lineup__35bwS ol li a").length'
            ) > 0
        )
    except Exception:
        # 전혀 안 뜨면 실패로 간주
        return [], []

    # 2) 두 팀의 ol을 순서대로 잡아 이름/이미지 src에서 playerId를 추출
    teams = driver.execute_script("""
        const out = [];
        const roots = Array.from(document.querySelectorAll("div.Lineup_comp_lineup__35bwS > div > div"));
        for (const root of roots.slice(0, 2)) {
          const arr = [];
          const items = root.querySelectorAll("ol li a");
          for (const a of items) {
            const nmEl = a.querySelector("strong,em,span");
            const name = (nmEl ? nmEl.textContent : a.textContent || "").trim();
            const img = a.querySelector("img");
            let pid = "";
            if (img && img.src) {
              try {
                const u = new URL(img.src, location.href);
                pid = u.searchParams.get("playerId") || "";
                if (!pid) {
                  // 일부 경우 src 경로 마지막 세그먼트가 id일 수 있음
                  const parts = u.pathname.split("/").filter(Boolean);
                  pid = parts.length ? parts[parts.length - 1].replace(/\\.\\w+$/, "") : "";
                }
              } catch(e) {}
            }
            if (!pid && a.href) {
              try { pid = new URL(a.href, location.href).searchParams.get("playerId") || ""; } catch(e) {}
            }
            if (name && pid) arr.push([name, pid]);
          }
          out.push(arr);
        }
        return out;
    """)

    team1 = teams[0] if len(teams) > 0 else []
    team2 = teams[1] if len(teams) > 1 else []

    # 3) 라인업이 '투수만 먼저 뜨는' 경우 방어:
    #    (목표는 '투수 + 9타자(총 10명)' 또는 '9타자' 형태. 0/1명이면 아직 미노출로 간주)
    if len(team1) <= 1:
        team1 = []
    if len(team2) <= 1:
        team2 = []

    return team1, team2

today = datetime.date.today()

# 기존 파일에서 마지막 저장된 날짜와 game_id 파악
last_date = None
max_game_id = 0
try:
    with open('data/lineups.csv', 'r', encoding='utf-8-sig') as f:
        reader = list(csv.DictReader(f))
        if reader:
            last_row = reader[-1]
            last_date = datetime.datetime.strptime(last_row['date'], '%Y%m%d').date()
            max_game_id = max(int(row['game_id']) for row in reader if row['game_id'].isdigit())
except FileNotFoundError:
    pass

# kbo_schedule.csv에서 오늘까지의 경기만 필터링하고 game_id 부여
with open('data/kbo_schedule.csv', 'r', encoding='utf-8-sig') as infile:
    reader = list(csv.DictReader(infile))
    game_map = {}
    game_info_map = {}
    game_id_lookup = {}
    game_id_counter = max_game_id + 1  # 새로 부여할 game_id 시작값

    for row in reader:
        date_str = row['day'].replace('.', '')
        game_date = datetime.datetime.strptime(date_str, '%Y%m%d').date()

        # 이미 저장된 날짜 이후의 경기만 처리
        if game_date > today or (last_date and game_date <= last_date):
            continue

        team1 = row['team1']
        team2 = row['team2']
        time_str = row['time']
        stadium = row.get('stadium', '')
        key = (date_str, team1, team2, time_str)

        game_map.setdefault((date_str, team1, team2), []).append(row)
        game_id_lookup[key] = game_id_counter
        game_info_map[key] = {'stadium': stadium, 'game_id': game_id_counter}
        game_id_counter += 1

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

# lineups.csv 파일에 이어서 저장
with open('data/lineups.csv', 'a', newline='', encoding='utf-8-sig') as outfile:
    writer = csv.writer(outfile)
    if last_date is None:
        writer.writerow(['date', 'batting_order', 'game_id', 'hitter_id', 'pitcher_id', 'stadium'])

    for key, games in game_map.items():
        games_sorted = sorted(games, key=lambda x: x['time'])  # 더블헤더 대비 시간순 정렬
        double_header_failed = False
        first_game_lineup1 = None
        first_game_lineup2 = None

        for idx, row in enumerate(games_sorted):
            date_str = row['day'].replace('.', '')
            time_str = row['time']
            team1 = row['team1']
            team2 = row['team2']
            team1_code = TEAM_CODE.get(team1, '')
            team2_code = TEAM_CODE.get(team2, '')

            if not team1_code or not team2_code:
                continue

            game_id = game_id_lookup.get((date_str, team1, team2, time_str))
            stadium = row.get('stadium', '')

            # 네이버 경기 ID 결정 (일반, 더블헤더 1/2차전 등)
            if len(games_sorted) == 1:
                naver_game_id = '02025'
            elif idx == 0:
                naver_game_id = '12025'
            else:
                naver_game_id = '22025' if not double_header_failed else '02025'

            debug(f"fetch lineup {date_str} {team1}-{team2} time:{time_str} naver:{naver_game_id} gid:{game_id}")
            team1_lineup, team2_lineup = get_lineup(date_str, team1_code, team2_code, naver_game_id, driver)
            debug(f"lineup len t1:{len(team1_lineup)} t2:{len(team2_lineup)}")

            # 더블헤더 첫 경기 실패 시 보정
            if len(games_sorted) > 1 and idx == 0 and not team1_lineup and not team2_lineup:
                double_header_failed = True
            elif len(games_sorted) > 1 and idx == 0:
                first_game_lineup1 = team1_lineup
                first_game_lineup2 = team2_lineup

            # 더블헤더 두 번째 경기 재시도
            if len(games_sorted) > 1 and idx == 1 and not team1_lineup and not team2_lineup and naver_game_id == '22025':
                team1_lineup, team2_lineup = get_lineup(date_str, team1_code, team2_code, '02025', driver)

            # 더블헤더 두 번째 경기: 첫 타자 삽입
            if len(games_sorted) > 1 and idx == 1:
                if len(team1_lineup) == 9 and first_game_lineup1:
                    team1_lineup.insert(0, first_game_lineup1[0])
                if len(team2_lineup) == 9 and first_game_lineup2:
                    team2_lineup.insert(0, first_game_lineup2[0])

            for i, (player_name, player_id) in enumerate(team1_lineup):
                if i == 0:
                    writer.writerow([date_str, 1, game_id, 1, player_id, stadium])
                else:
                    writer.writerow([date_str, i + 1, game_id, player_id, 1, stadium])

            for i, (player_name, player_id) in enumerate(team2_lineup):
                if i == 0:
                    writer.writerow([date_str, 1, game_id, 1, player_id, stadium])
                else:
                    writer.writerow([date_str, i + 1, game_id, player_id, 1, stadium])

            time.sleep(1.5)

# 브라우저 종료
driver.quit()
