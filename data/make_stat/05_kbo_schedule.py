from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import datetime
import os  # os 모듈 추가

# --- 기존 TEAM_CODE, format_date 함수 등은 동일하게 유지 ---
TEAM_CODE = {
    '롯데': 'LT', 'KIA': 'HT', 'LG': 'LG', '두산': 'OB', 'SSG': 'SK',
    '키움': 'WO', '삼성': 'SS', '한화': 'HH', 'KT': 'KT', 'NC': 'NC',
}

def format_date(day_str, year=2025):
    day_clean = re.sub(r'\(.*\)', '', day_str).strip()
    month, day = day_clean.split('.')
    return f"{year}.{month.zfill(2)}.{day.zfill(2)}"

# --- 스크래핑 로직 수정 ---
CSV_PATH = "data/kbo_schedule.csv"
start_date = datetime.date(2025, 3, 1) # 기본 시작 날짜 (시즌 시작 전)

# 1. 기존 CSV 파일 확인 및 마지막 경기 날짜 조회
if os.path.exists(CSV_PATH):
    try:
        existing_df = pd.read_csv(CSV_PATH)
        existing_df['day'] = pd.to_datetime(existing_df['day'], format='%Y.%m.%d')
        
        # 경기 결과가 있는 ('승', '패', '무') 행만 필터링
        result_df = existing_df[existing_df['team1_result'].isin(['승', '패', '무'])].copy()
        
        if not result_df.empty:
            # 경기 결과가 있는 마지막 날짜를 시작 날짜로 설정
            last_game_date = result_df['day'].max().date()
            start_date = last_game_date
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # 파일이 없거나 비어있으면 기본 시작 날짜 사용
        pass

print(f"데이터 수집 시작 날짜: {start_date}")

url = 'https://www.koreabaseball.com/Schedule/Schedule.aspx'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

all_schedules = []

# 2. 마지막 경기 날짜가 포함된 월부터 스크래핑 시작
for month in range(start_date.month, 11):  # 10월까지로 범위 확장 (포스트시즌 고려)
    month_str = str(month).zfill(2)
    select = Select(driver.find_element(By.ID, 'ddlMonth'))
    select.select_by_value(month_str)

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tbl-type06')))
        tbody = driver.find_element(By.CSS_SELECTOR, '#tblScheduleList > tbody')
        rows = tbody.find_elements(By.TAG_NAME, 'tr')

        # --- (데이터 파싱 부분은 기존과 거의 동일) ---
        current_day = None
        for row in rows:
            try:
                day_td = row.find_element(By.CSS_SELECTOR, 'td.day')
                current_day = day_td.text.strip()
            except:
                pass
            
            if not current_day:
                continue

            day_str = format_date(current_day)
            game_date = datetime.datetime.strptime(day_str, "%Y.%m.%d").date()

            # 3. 이미 결과가 있는 날짜의 경기는 건너뛰기
            if game_date < start_date:
                continue
            
            # 오늘 날짜 이후의 경기 중, start_date와 같은 날짜의 경기는 중복 수집될 수 있으므로 추가
            # (예: 8/11 경기가 '결과 없음'으로 저장된 상태에서 다시 스크립트 실행 시)
            if game_date == start_date and datetime.date.today() > game_date:
                 pass # 단, 이 경우 아래 저장 로직에서 중복제거가 핸들해줌

            time_td = row.find_element(By.CSS_SELECTOR, 'td.time')
            time_val = time_td.text.strip()

            play_cell = row.find_element(By.CLASS_NAME, 'play')
            spans = play_cell.find_elements(By.TAG_NAME, 'span')
            em = play_cell.find_element(By.TAG_NAME, 'em')

            team_names = [span.text.strip() for span in spans if span.text.strip() not in ['vs', ''] and span.get_attribute('class') not in ['win', 'lose', 'same']]
            scores = em.text.strip().split('vs')
            scores = [s.strip() for s in scores] if len(scores) == 2 else ['', '']

            if len(team_names) != 2:
                continue

            t1, t2 = team_names[0], team_names[1]
            s1, s2 = (scores[0] if scores[0].isdigit() else ''), (scores[1] if scores[1].isdigit() else '')
            
            r1, r2 = '', ''
            today = datetime.datetime.today().date()
            if s1 and s2:
                try:
                    if int(s1) > int(s2): r1, r2 = '승', '패'
                    elif int(s1) < int(s2): r1, r2 = '패', '승'
                    else: r1, r2 = '무', '무'
                except ValueError: pass
            elif game_date < today:
                r1 = r2 = '취소'

            tds = row.find_elements(By.TAG_NAME, 'td')
            stadium = tds[6].text.strip()
            note = tds[7].text.strip()
            if not stadium and note:
                stadium = note
                note = '-'
            if note and note != '-':
                r1 = r2 = '취소'

            all_schedules.append({
                'day': day_str, 'time': time_val,
                'team1': TEAM_CODE.get(t1, t1), 'team1_score': s1, 'team1_result': r1,
                'team2': TEAM_CODE.get(t2, t2), 'team2_score': s2, 'team2_result': r2,
                'stadium': stadium, 'note': note,
            })

    except Exception as e:
        print(f"{month}월 스크래핑 중 오류 발생: {e}")
        pass

driver.quit()

# 4. 데이터 병합 및 저장
if all_schedules:
    new_df = pd.DataFrame(all_schedules)
    
    # 기존 데이터와 새 데이터 병합
    if os.path.exists(CSV_PATH) and not existing_df.empty:
        # 날짜 형식을 다시 문자열로 통일
        existing_df['day'] = existing_df['day'].dt.strftime('%Y.%m.%d')
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        final_df = new_df

    # 5. 중복 데이터 제거 (날짜, 팀1, 팀2가 같으면 중복으로 간주) 및 정렬
    final_df.drop_duplicates(subset=['day', 'team1', 'team2'], keep='last', inplace=True)
    final_df.sort_values(by=['day', 'time'], inplace=True)
    
    final_df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"총 {len(final_df)}개의 경기 일정을 {CSV_PATH}에 저장했습니다.")
else:
    print("새로 추가할 경기 일정이 없습니다.")
