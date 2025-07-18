from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import datetime
import os
import sys
import django

# Django 환경 설정
sys.path.append('/Users/m2/Desktop/tothe_ballpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baseball.settings')
django.setup()

from cal.models import Game

# --- 팀 코드 매핑 ---
TEAM_CODE = {
    '롯데': 'LT', 'KIA': 'HT', 'LG': 'LG', '두산': 'OB', 'SSG': 'SK',
    '키움': 'WO', '삼성': 'SS', '한화': 'HH', 'KT': 'KT', 'NC': 'NC',
}

# --- 날짜 포맷 함수 ---
def format_date(day_str, year=2025):
    day_clean = re.sub(r'\(.*\)', '', day_str).strip()
    month, day = day_clean.split('.')
    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

# --- 스크래핑 설정 ---
url = 'https://www.koreabaseball.com/Schedule/Schedule.aspx'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

# --- 스크래핑 및 DB 저장 ---
for month in range(3, 10):
    month_str = str(month).zfill(2)
    select = Select(driver.find_element(By.ID, 'ddlMonth'))
    select.select_by_value(month_str)
    time.sleep(2)

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tbl-type06')))
        tbody = driver.find_element(By.CSS_SELECTOR, '#tblScheduleList > tbody')
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        current_day = None

        for row in rows:
            try:
                day_td = row.find_element(By.CSS_SELECTOR, 'td.day')
                current_day = day_td.text.strip()
            except:
                pass

            try:
                time_str = row.find_element(By.CSS_SELECTOR, 'td.time').text.strip()
            except:
                continue
            game_date = format_date(current_day)

            play_cell = row.find_element(By.CLASS_NAME, 'play')
            spans = play_cell.find_elements(By.TAG_NAME, 'span')
            team_names = [span.text.strip() for span in spans if span.text.strip() not in ['vs', ''] and span.get_attribute('class') not in ['win', 'lose', 'same']]
            
            if len(team_names) != 2:
                continue

            scores_text = play_cell.find_element(By.TAG_NAME, 'em').text.strip()
            scores = [s.strip() for s in scores_text.split('vs')] if 'vs' in scores_text else [None, None]

            t1_code = TEAM_CODE.get(team_names[0], team_names[0])
            t2_code = TEAM_CODE.get(team_names[1], team_names[1])
            s1 = int(scores[0]) if scores[0] and scores[0].isdigit() else None
            s2 = int(scores[1]) if scores[1] and scores[1].isdigit() else None

            r1, r2 = '', ''
            today = datetime.date.today()
            game_datetime = datetime.datetime.strptime(game_date, "%Y-%m-%d").date()

            if s1 is not None and s2 is not None:
                if s1 > s2: r1, r2 = '승', '패'
                elif s1 < s2: r1, r2 = '패', '승'
                else: r1, r2 = '무', '무'
            elif game_datetime < today:
                r1, r2 = '취소', '취소'

            tds = row.find_elements(By.TAG_NAME, 'td')
            stadium = tds[6].text.strip()
            note = tds[7].text.strip()
            if not stadium and note: stadium, note = note, '-'
            if note and note != '-': r1, r2 = '취소', '취소'

            game_data = {
                'time': time_str,
                'team1': t1_code,
                'team2': t2_code,
                'team1_score': s1,
                'team2_score': s2,
                'team1_result': r1,
                'team2_result': r2,
                'stadium': stadium,
                'note': note,
            }

            Game.objects.update_or_create(
                date=game_date,
                time=time_str,
                team1=t1_code,
                team2=t2_code,
                defaults=game_data
            )

    except Exception as e:
        print(f"Error processing month {month}: {e}")

driver.quit()
print("KBO schedule updated successfully.")