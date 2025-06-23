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

# 팀 코드 매핑
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

# 날짜 포맷 함수
def format_date(day_str, year=2025):
    day_clean = re.sub(r'\(.*\)', '', day_str).strip()
    month, day = day_clean.split('.')
    return f"{year}.{month.zfill(2)}.{day.zfill(2)}"

# Selenium 설정
url = 'https://www.koreabaseball.com/Schedule/Schedule.aspx'
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)
driver.get(url)

all_schedules = []

for month in range(3, 10):  # 3월부터 9월까지
    month_str = str(month).zfill(2)
    select = Select(driver.find_element(By.ID, 'ddlMonth'))
    select.select_by_value(month_str)

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tbl-type06')))
        tbody = driver.find_element(By.CSS_SELECTOR, '#tblScheduleList > tbody')
        rows = tbody.find_elements(By.TAG_NAME, 'tr')

        days, times, plays, stadiums, notes = [], [], [], [], []
        team1s, team1_scores, team1_results = [], [], []
        team2s, team2_scores, team2_results = [], [], []
        current_day = None

        for row in rows:
            try:
                day_td = row.find_element(By.CSS_SELECTOR, 'td.day')
                current_day = day_td.text.strip()
            except:
                pass

            time_td = row.find_element(By.CSS_SELECTOR, 'td.time')
            time = time_td.text.strip()
            day = format_date(current_day)

            play_cell = row.find_element(By.CLASS_NAME, 'play')
            spans = play_cell.find_elements(By.TAG_NAME, 'span')
            em = play_cell.find_element(By.TAG_NAME, 'em')

            # 팀 이름 필터링
            team_names = [span.text.strip() for span in spans if span.text.strip() not in ['vs', ''] and span.get_attribute('class') not in ['win', 'lose', 'same']]
            scores = em.text.strip().split('vs')
            scores = [s.strip() for s in scores] if len(scores) == 2 else ['', '']

            # play 문자열 생성
            if len(team_names) == 2:
                if scores[0] and scores[1]:
                    play = f"{team_names[0]} {scores[0]} vs {scores[1]} {team_names[1]}"
                else:
                    play = f"{team_names[0]} vs {team_names[1]}"
            else:
                play = em.text.strip()

            # 승/패/무 계산
            t1 = team_names[0] if len(team_names) > 0 else ''
            t2 = team_names[1] if len(team_names) > 1 else ''
            s1 = scores[0] if scores[0].isdigit() else ''
            s2 = scores[1] if scores[1].isdigit() else ''

            today = datetime.datetime.today().date()
            try:
                game_date = datetime.datetime.strptime(day, "%Y.%m.%d").date()
            except Exception:
                game_date = today

            if s1 and s2:
                try:
                    s1_i = int(s1)
                    s2_i = int(s2)
                    if s1_i > s2_i:
                        r1, r2 = '승', '패'
                    elif s1_i < s2_i:
                        r1, r2 = '패', '승'
                    else:
                        r1 = r2 = '무'
                except ValueError:
                    r1 = r2 = ''
            else:
                if game_date < today:
                    r1 = r2 = '취소'
                else:
                    r1 = r2 = ''

            # 경기장 및 비고
            tds = row.find_elements(By.TAG_NAME, 'td')
            stadium = tds[6].text.strip()
            note = tds[7].text.strip()
            if not stadium and note:
                stadium = note
                note = '-'
            if note and note != '-':
                r1 = r2 = '취소'

            # 팀 이름을 팀 코드로 변환
            t1_code = TEAM_CODE.get(t1, t1)
            t2_code = TEAM_CODE.get(t2, t2)

            # 데이터 저장
            days.append(day)
            times.append(time)
            team1s.append(t1_code)
            team1_scores.append(s1)
            team1_results.append(r1)
            team2s.append(t2_code)
            team2_scores.append(s2)
            team2_results.append(r2)
            stadiums.append(stadium)
            notes.append(note)

        df = pd.DataFrame({
            'day': days,
            'time': times,
            'team1': team1s,
            'team1_score': team1_scores,
            'team1_result': team1_results,
            'team2': team2s,
            'team2_score': team2_scores,
            'team2_result': team2_results,
            'stadium': stadiums,
            'note': notes,
        })

        all_schedules.append(df)

    except Exception as e:
        print(f"[{month_str}월] 크롤링 실패: {e}")

# 전체 결과 저장
if all_schedules:
    final_df = pd.concat(all_schedules, ignore_index=True)
    final_df.to_csv("data/kbo_schedule.csv", index=False, encoding='utf-8-sig')

driver.quit()
