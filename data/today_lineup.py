import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

TEAM_CODE = {
    '롯데': 'LT',
    'KIA': 'HT',
    'LG': 'LG',
    '두산': 'OB',
    'SSG': 'SK',
    '키움': 'WO',
    '삼성': 'SS',
    '한화': 'HH',
    'KT': 'KT',
    'NC': 'NC',
}

def get_lineup(today, team1_code, team2_code, game_id, driver):
    url = f'https://m.sports.naver.com/game/{today}{team1_code}{team2_code}{game_id}/lineup'
    driver.get(url)
    time.sleep(2.5)
    try:
        lineup_boxes = driver.find_elements(By.CSS_SELECTOR, 'div.Lineup_comp_lineup__361i1 > div > div')
        team1 = []
        team2 = []
        for idx, team_box in enumerate(lineup_boxes[:2]):
            players = team_box.find_elements(By.CSS_SELECTOR, 'ol > li > a > div > strong')
            player_names = [player.text for player in players]
            if idx == 0:
                team1 = player_names
            else:
                team2 = player_names
        return team1, team2
    except Exception as e:
        print(f"라인업 크롤링 실패: {e}")
        return [], []

# 오늘 날짜
today_str = datetime.today().strftime("%Y.%m.%d")
today_str_csv = datetime.today().strftime("%Y%m%d")

# 이미 저장된 라인업 읽기 (중복 방지)
saved_games = set()
try:
    with open('lineups.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['date'], row['team1'], row['team2'])
            saved_games.add(key)
except FileNotFoundError:
    pass

# 오늘 경기만 추출
today_games = []
with open('kbo_schedule.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['day'] == today_str:
            today_games.append(row)

if not today_games:
    print("오늘 경기 없음")
    exit()

# (날짜, 팀1, 팀2)별로 시간순 정렬 후 game_id 부여
game_map = {}
for row in today_games:
    date_str = row['day'].replace('.', '')
    team1 = row['team1']
    team2 = row['team2']
    key = (date_str, team1, team2)
    game_map.setdefault(key, []).append(row)

driver = webdriver.Chrome()

# ...existing code...

with open('lineups.csv', 'a', newline='', encoding='utf-8-sig') as outfile, \
     open('today_lineup_flatten.csv', 'w', newline='', encoding='utf-8-sig') as flatfile:
    writer = csv.writer(outfile)
    flat_writer = csv.writer(flatfile)
    flat_writer.writerow(['date', 'time', 'team1', 'team2', 'team1_player', 'team2_player'])

    for key, games in game_map.items():
        games_sorted = sorted(games, key=lambda x: x['time'])
        double_header_failed = False
        for idx, row in enumerate(games_sorted):
            date_str = row['day'].replace('.', '')
            time_str = row['time']
            team1 = row['team1']
            team2 = row['team2']
            team1_code = TEAM_CODE.get(team1, '')
            team2_code = TEAM_CODE.get(team2, '')
            if not team1_code or not team2_code:
                print(f"팀 코드 없음: {team1}, {team2}")
                continue

            # 중복 방지
            if (date_str, team1, team2) in saved_games:
                print(f"이미 저장됨: {date_str} {team1} vs {team2}")
                continue

            # game_id 결정
            if len(games_sorted) == 1:
                game_id = '02025'
            elif idx == 0:
                game_id = '12025'
            else:
                if double_header_failed:
                    game_id = '02025'
                else:
                    game_id = '22025'

            print(f"크롤링: {date_str} {team1} vs {team2} ({time_str}) game_id={game_id}")

            team1_lineup, team2_lineup = get_lineup(date_str, team1_code, team2_code, game_id, driver)

            # 첫 경기(12025)에서 라인업이 없으면 flag ON
            if len(games_sorted) > 1 and idx == 0 and not team1_lineup and not team2_lineup:
                double_header_failed = True

            # 두 번째 경기에서 22025로도 라인업이 없으면 02025로 한 번 더 시도
            if len(games_sorted) > 1 and idx == 1 and not team1_lineup and not team2_lineup and game_id == '22025':
                print("22025 라인업 없음, 02025로 재시도")
                team1_lineup, team2_lineup = get_lineup(date_str, team1_code, team2_code, '02025', driver)

            writer.writerow([
                date_str, time_str, team1, team2,
                ','.join(team1_lineup),
                ','.join(team2_lineup)
            ])

            # 1:1 매칭(flatten) 저장
            max_len = max(len(team1_lineup), len(team2_lineup))
            team1_lineup += [''] * (max_len - len(team1_lineup))
            team2_lineup += [''] * (max_len - len(team2_lineup))
            for p1, p2 in zip(team1_lineup, team2_lineup):
                flat_writer.writerow([date_str, time_str, team1, team2, p1, p2])

            time.sleep(1.5)

driver.quit()
print("✅ 오늘 경기 라인업 저장 완료 (today_lineup_flatten.csv 포함)")