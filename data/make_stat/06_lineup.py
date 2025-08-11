import pandas as pd
import time
import datetime
import os
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# KBO 팀 코드 매핑
TEAM_CODE = {
    'LT': 'LT', 'HT': 'HT', 'LG': 'LG', 'OB': 'OB', 'SK': 'SK',
    'WO': 'WO', 'SS': 'SS', 'HH': 'HH', 'KT': 'KT', 'NC': 'NC',
}

# 네이버 스포츠 라인업 스크래핑 함수 (기존과 동일)
def get_lineup(url, driver):
    driver.get(url)
    time.sleep(1.5) # 페이지 로딩 대기
    try:
        lineup_boxes = driver.find_elements(By.CSS_SELECTOR, 'div.Lineup_comp_lineup__361i1 > div > div')
        team1_lineup, team2_lineup = [], []
        for idx, team_box in enumerate(lineup_boxes[:2]):
            players = team_box.find_elements(By.CSS_SELECTOR, 'ol > li > a')
            player_info = []
            for player in players:
                name = player.find_element(By.CSS_SELECTOR, 'div > strong').text.strip()
                href = player.get_attribute('href')
                player_id = parse_qs(urlparse(href).query).get('playerId', [''])[0] if href else ''
                player_info.append((name, player_id))
            if idx == 0: team1_lineup = player_info
            else: team2_lineup = player_info
        return team1_lineup, team2_lineup
    except Exception:
        return [], []

# --- 데이터 처리 로직 (Pandas 중심으로 재구성) ---
SCHEDULE_CSV_PATH = 'data/kbo_schedule.csv'
LINEUPS_CSV_PATH = 'data/lineups.csv'

# 1. 필요한 CSV 파일 로드
try:
    schedule_df = pd.read_csv(SCHEDULE_CSV_PATH)
except FileNotFoundError:
    print(f"{SCHEDULE_CSV_PATH} 파일이 없습니다. 05_kbo_schedule.py를 먼저 실행하세요.")
    exit()

existing_lineups_df = pd.DataFrame()
if os.path.exists(LINEUPS_CSV_PATH):
    try:
        existing_lineups_df = pd.read_csv(LINEUPS_CSV_PATH)
    except pd.errors.EmptyDataError:
        pass # 파일이 비어있으면 그냥 진행

# 2. 처리할 경기 목록 필터링
# 오늘 날짜 이전의 경기 중, 경기 결과가 있고, 아직 lineups.csv에 없는 경기를 대상
schedule_df['date_dt'] = pd.to_datetime(schedule_df['day'], format='%Y.%m.%d')
schedule_df = schedule_df[schedule_df['date_dt'] <= datetime.datetime.now()].copy()
schedule_df = schedule_df[schedule_df['team1_result'].isin(['승', '패', '무'])].copy()

# game_id 부여 (kbo_schedule.csv의 index를 임시 game_id로 활용)
schedule_df['game_id'] = schedule_df.index

if not existing_lineups_df.empty:
    processed_game_ids = existing_lineups_df['game_id'].unique()
    target_games_df = schedule_df[~schedule_df['game_id'].isin(processed_game_ids)]
else:
    target_games_df = schedule_df

if target_games_df.empty:
    print("새로 수집할 라인업이 없습니다.")
    exit()

print(f"총 {len(target_games_df)}개의 새로운 경기에 대한 라인업을 수집합니다.")

# 3. 라인업 스크래핑 실행
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

new_lineups = []
# 날짜별, 팀별로 그룹화하여 더블헤더 처리
for (date_str, team1, team2), games in target_games_df.groupby(['day', 'team1', 'team2']):
    games_sorted = games.sort_values(by='time')
    
    for idx, row in games_sorted.iterrows():
        date_url = row['day'].replace('.', '')
        team1_code = TEAM_CODE.get(row['team1'], '')
        team2_code = TEAM_CODE.get(row['team2'], '')
        game_id = row['game_id']
        stadium = row['stadium']

        if not team1_code or not team2_code:
            continue

        # 네이버 경기 ID 결정 (일반: 0, 더블헤더: 1, 2)
        naver_game_suffix = '0'
        if len(games_sorted) > 1:
            naver_game_suffix = str(idx + 1)

        url = f'https://m.sports.naver.com/game/{date_url}{team1_code}{team2_code}{naver_game_suffix}2025/lineup'
        team1_lineup, team2_lineup = get_lineup(url, driver)

        # 라인업 데이터 저장
        for i, (name, p_id) in enumerate(team1_lineup):
            is_pitcher = 1 if i == 0 else 0 # 첫번째는 투수로 가정
            new_lineups.append({
                'date': date_url, 'batting_order': i if is_pitcher else i + 1,
                'game_id': game_id, 'hitter_id': '' if is_pitcher else p_id,
                'pitcher_id': p_id if is_pitcher else '', 'stadium': stadium
            })
        
        for i, (name, p_id) in enumerate(team2_lineup):
            is_pitcher = 1 if i == 0 else 0
            new_lineups.append({
                'date': date_url, 'batting_order': i if is_pitcher else i + 1,
                'game_id': game_id, 'hitter_id': '' if is_pitcher else p_id,
                'pitcher_id': p_id if is_pitcher else '', 'stadium': stadium
            })

driver.quit()

# 4. 기존 데이터와 새 데이터 병합, 중복 제거 후 저장
if new_lineups:
    new_lineups_df = pd.DataFrame(new_lineups)
    
    # 컬럼 순서 및 타입 통일
    final_df = pd.concat([existing_lineups_df, new_lineups_df], ignore_index=True)
    final_df.drop_duplicates(subset=['game_id', 'hitter_id', 'pitcher_id', 'batting_order'], keep='last', inplace=True)
    final_df.sort_values(by=['date', 'game_id'], inplace=True)
    
    # 컬럼 순서 정의
    final_df = final_df[['date', 'batting_order', 'game_id', 'hitter_id', 'pitcher_id', 'stadium']]

    final_df.to_csv(LINEUPS_CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"총 {len(final_df)}개의 라인업 정보를 {LINEUPS_CSV_PATH}에 저장했습니다.")
else:
    print("새로 추가된 라인업이 없습니다.")
