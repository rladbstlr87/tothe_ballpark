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

from cal.models import Pitcher

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
base_url = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx"
detail_url = "https://www.koreabaseball.com/Record/Player/PitcherDetail/Basic.aspx?playerId={}"

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
            table1 = soup.select_one("div.tbl-type02.tbl-type02-pd0.mb35 > table > tbody")
            data1 = [td.text.strip() for td in table1.select("td")][1:]
        except:
            data1 = []

        try:
            table2 = soup.select_one("div.player_records > div:nth-child(4) > table > tbody")
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
    if isinstance(value, str) and '.' in value and target_type == int:
        return int(float(value))
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return target_type(0)

for row in final_data:
    # 스크래핑된 컬럼 순서:
    # 0: team, 1: player_id, 2: player_name, 3: ERA, 4: G, 5: CG, 6: SHO, 7: W, 8: L, 9: SV, 10: HLD,
    # 11: WPCT, 12: TBF, 13: NP, 14: IP, 15: H, 16: 2B, 17: 3B, 18: HR, 19: SAC, 20: SF, 21: BB,
    # 22: IBB, 23: SO, 24: WP, 25: BK, 26: R, 27: ER, 28: BSV, 29: WHIP, 30: AVG, 31: QS
    ip_str = row[14]
    ip_parts = ip_str.split(' ')
    ip_total = 0.0
    try:
        if len(ip_parts) == 2:
            ip_total = float(ip_parts[0]) + (float(ip_parts[1].split('/')[0]) / 3.0)
        elif ' ' in ip_str: # "1 1/3" 같은 형태
            parts = ip_str.split(' ')
            ip_total = float(parts[0]) + (float(parts[1].split('/')[0]) / 3.0)
        elif '/' in ip_str: # "1/3" 같은 형태
            parts = ip_str.split('/')
            ip_total = float(parts[0]) / float(parts[1])
        elif ip_str and ip_str != '-':
            ip_total = float(ip_str)
    except ValueError:
        ip_total = 0.0

    data_for_model = {
        'team_name': row[0],
        'player_name': row[2],
        'ERA': clean_value(row[3], float),
        'G': clean_value(row[4], int),
        'CG': clean_value(row[5], int),
        'SHO': clean_value(row[6], int),
        'W': clean_value(row[7], int),
        'L': clean_value(row[8], int),
        'SV': clean_value(row[9], int),
        'HLD': clean_value(row[10], int),
        'WPCT': clean_value(row[11], float),
        'TBF': clean_value(row[12], int),
        'NP': clean_value(row[13], int),
        'IP': ip_total,
        'H': clean_value(row[15], int),
        'H_2B': clean_value(row[16], int),
        'H_3B': clean_value(row[17], int),
        'HR': clean_value(row[18], int),
        'SAC': clean_value(row[19], int),
        'SF': clean_value(row[20], int),
        'BB': clean_value(row[21], int),
        'IBB': clean_value(row[22], int),
        'SO': clean_value(row[23], int),
        'WP': clean_value(row[24], int),
        'BK': clean_value(row[25], int),
        'R': clean_value(row[26], int),
        'ER': clean_value(row[27], int),
        'BSV': clean_value(row[28], int),
        'WHIP': clean_value(row[29], float),
        'AVG': clean_value(row[30], float),
        'QS': clean_value(row[31], int),
    }

    Pitcher.objects.update_or_create(
        player_id=row[1],
        defaults=data_for_model
    )

# 임시 선수 추가
dummy_data = {
    'player_name': '임시선수', 'team_name': 'TMP',
    'ERA': 3.21, 'G': 10, 'CG': 0, 'SHO': 0, 'W': 2, 'L': 1, 'SV': 1, 'HLD': 0, 'WPCT': 0.667, 'TBF': 150, 'NP': 1000, 'IP': 55.1, 'H': 48, 'H_2B': 5, 'H_3B': 0, 'HR': 3,
    'SAC': 2, 'SF': 1, 'BB': 12, 'IBB': 1, 'SO': 35, 'WP': 1, 'BK': 0, 'R': 15, 'ER': 12, 'BSV': 0, 'WHIP': 1.25, 'AVG': 0.220, 'QS': 2
}
Pitcher.objects.update_or_create(
    player_id='1',
    defaults=dummy_data
)

print("Pitcher stats updated successfully.")