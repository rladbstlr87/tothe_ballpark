import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from django.db import transaction
import os
import sys
import django

# Django 환경 설정
sys.path.append('/Users/m2/Desktop/tothe_ballpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baseball.settings')
django.setup()
from cal.models import Pitcher


# --- 스크래핑 설정 ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

# --- 데이터베이스에서 선수 ID 가져오기 ---
pitchers = list(Pitcher.objects.all())
pitcher_map = {p.player_id: p for p in pitchers}

# --- 스크래핑 및 DB 업데이트 ---
updated_pitchers = []
for pid in pitcher_map.keys():
    # if pid == 1:
    #     continue
    url = f"https://m.sports.naver.com/player/index?from=sports&playerId={pid}&category=kbo&tab=record"
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    speed_value = 0
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#record_04 > div > div > table > thead > tr > th:nth-child(2)')))

        try:
            ths = driver.find_elements(By.CSS_SELECTOR, '#record_04 > div > div > table > thead > tr > th')

            fastball_idx = None
            for idx, th in enumerate(ths):
                if '직구' in th.text:
                    fastball_idx = idx + 1
                    break

            if fastball_idx is None:
                for idx, th in enumerate(ths):
                    if '투심' in th.text:
                        fastball_idx = idx + 1
                        break

            if fastball_idx is not None:
                value_xpath = f'//*[@id="record_04"]/div/div/table/tbody/tr[1]/td[{fastball_idx}]'
                value = driver.find_element(By.XPATH, value_xpath).text.strip()
                speed_value = value.split('k')[0]

        except Exception as e:
            speed_value = 130
    except UnexpectedAlertPresentException:
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            print(f'[Alert] Alert already gone for player {pid}, continuing.')
        continue
    if speed_value:
        try:
            speed_value = int(float(speed_value))
        except (ValueError, TypeError):
            speed_value = 130
            print(f"Could not convert speed '{speed_value}' to int for player {pid}")

    pitcher = pitcher_map[pid]
    pitcher.speed = speed_value
    updated_pitchers.append(pitcher)

driver.quit()

with transaction.atomic():
    Pitcher.objects.bulk_update(updated_pitchers, ['speed'])

print("Pitcher velocity update completed.")