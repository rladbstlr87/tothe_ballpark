import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import sys
import django

# Django 환경 설정
sys.path.append('/Users/m2/Desktop/tothe_ballpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baseball.settings')
django.setup()

from cal.models import Hitter

# --- 스크래핑 설정 ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

headers = {
    "User-Agent": "Mozilla/5.0"
}

teams = ["LG", "HH", "LT", "SS", "SK", "NC", "OB", "HT", "KT", "WO"]
base_url = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT"
detail_url = "https://www.koreabaseball.com/Record/Player/HitterDetail/Basic.aspx?playerId={}"

final_data = []

# --- 스크래핑 로직 ---
driver.get(base_url)

for team in teams:
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
    )
    select = Select(select_element)
    select.select_by_value(team)
    time.sleep(2)

    def collect_player_infos():
        players = driver.find_elements(By.CSS_SELECTOR,
            "#cphContents_cphContents_cphContents_udpContent > div.record_result > table > tbody > tr > td:nth-child(2) > a"
        )
        return [
            (a.get_attribute("href").split("playerId=")[-1], a.text.strip())
            for a in players
        ]

    player_infos = collect_player_infos()

    try:
        next_btn = driver.find_element(By.ID, "cphContents_cphContents_cphContents_ucPager_btnNo2")
        next_btn.click()
        time.sleep(2)
        player_infos += collect_player_infos()
        prev_btn = driver.find_element(By.ID, "cphContents_cphContents_cphContents_ucPager_btnNo1")
        prev_btn.click()
        time.sleep(2)
    except:
        pass

    team_data = []
    for player_id, player_name in player_infos:
        url = detail_url.format(player_id)
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")

        try:
            table1 = soup.select_one("div.tbl-type02.mb10 > table > tbody")
            data1 = [td.text.strip() for td in table1.select("td")][1:]
        except:
            data1 = []

        try:
            all_tables = soup.select("div.player_records > div > table")
            table2 = all_tables[1].select("tbody")[0]
            data2 = [td.text.strip() for td in table2.select("td")]
        except:
            data2 = []

        if data1 and data2:
            row = [team, player_id, player_name] + data1 + data2
            team_data.append(row)
        time.sleep(0.3)
    final_data.extend(team_data)

driver.quit()

# --- 데이터 처리 및 DB 저장 ---
def clean_value(value, target_type):
    if isinstance(value, str) and value in ('-', '', ' '):
        return target_type(0)
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return target_type(0)

for row in final_data:
    # 스크래핑된 컬럼 순서:
    # 0: team, 1: player_id, 2: player_name, 3: AVG, 4: G, 5: PA, 6: AB, 7: R, 8: H,
    # 9: 2B, 10: 3B, 11: HR, 12: TB, 13: RBI, 14: SB, 15: CS, 16: SAC, 17: SF,
    # 18: BB, 19: IBB, 20: HBP, 21: SO, 22: GDP, 23: SLG, 24: OBP, 25: E,
    # 26: SB%, 27: MH, 28: OPS, 29: RISP, 30: PH-BA
    sb = clean_value(row[14], int)
    cs = clean_value(row[15], int)

    data_for_model = {
        'team_name': row[0],
        'player_name': row[2],
        'AVG': clean_value(row[3], float),
        'G': clean_value(row[4], int),
        'PA': clean_value(row[5], int),
        'AB': clean_value(row[6], int),
        'R': clean_value(row[7], int),
        'H': clean_value(row[8], int),
        'H_2B': clean_value(row[9], int),
        'H_3B': clean_value(row[10], int),
        'HR': clean_value(row[11], int),
        'TB': clean_value(row[12], int),
        'RBI': clean_value(row[13], int),
        'SB': sb,
        'CS': cs,
        'SAC': clean_value(row[16], int),
        'SF': clean_value(row[17], int),
        'BB': clean_value(row[18], int),
        'IBB': clean_value(row[19], int),
        'HBP': clean_value(row[20], int),
        'SO': clean_value(row[21], int),
        'GDP': clean_value(row[22], int),
        'SLG': clean_value(row[23], float),
        'OBP': clean_value(row[24], float),
        'MH': clean_value(row[27], int),
        'OPS': clean_value(row[28], float),
        'RISP': clean_value(row[29], float),
        'PH_BA': clean_value(row[30], float),
        'SBA': sb + cs,
    }

    Hitter.objects.update_or_create(
        player_id=row[1],
        defaults=data_for_model
    )

# 임시 선수 추가
dummy_data = {
    'player_name': '임시선수', 'team_name': 'TMP',
    'AVG': 0.300, 'G': 100, 'PA': 400, 'AB': 370, 'R': 50, 'H': 111, 'H_2B': 20, 'H_3B': 1, 'HR': 15, 'TB': 180, 'RBI': 60, 'SB': 5, 'CS': 2, 'SAC': 3, 'SF': 5,
    'BB': 40, 'IBB': 5, 'HBP': 2, 'SO': 30, 'GDP': 3, 'SLG': 0.450, 'OBP': 0.380, 'MH': 25, 'OPS': 0.830, 'RISP': 0.289, 'PH_BA': 0.250,
    'SBA': 7
}
Hitter.objects.update_or_create(
    player_id='1',
    defaults=dummy_data
)

print("Hitter stats updated successfully.")