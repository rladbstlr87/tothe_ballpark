import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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

columns = [
    "team", "player_id", "player_name",
    "AVG", "G", "PA", "AB", "R", "H", "2B", "3B", "HR", "TB", "RBI", "SB", "CS", "SAC", "SF",
    "BB", "IBB", "HBP", "SO", "GDP", "SLG", "OBP", "E", "SB%", "MH", "OPS", "RISP", "PH-BA"
]

driver.get(base_url)

# 각 팀별로 반복
for team in teams:

    # 팀 선택
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
    )
    select = Select(select_element)
    select.select_by_value(team)
    time.sleep(2)

    # 선수 정보 수집 함수
    def collect_player_infos():
        players = driver.find_elements(By.CSS_SELECTOR,
            "#cphContents_cphContents_cphContents_udpContent > div.record_result > table > tbody > tr > td:nth-child(2) > a"
        )
        return [
            (a.get_attribute("href").split("playerId=")[-1], a.text.strip())
            for a in players
        ]

    # 1페이지 선수 수집
    player_infos = collect_player_infos()

    # 2페이지가 있다면 수집
    try:
        next_btn = driver.find_element(By.ID, "cphContents_cphContents_cphContents_ucPager_btnNo2")
        next_btn.click()
        time.sleep(2)

        player_infos += collect_player_infos()

        # 1페이지로 복귀
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

# 임시 선수 추가
dummy_row = [
    "TMP", "1", "임시선수",
    "0.300", 100, 400, 370, 50, 111, 20, 1, 15, 180, 60, 5, 2, 3, 5,
    40, 5, 2, 30, 3, 0.450, 0.380, 2, "0.714", 25, 0.830, 0.289, 0.250
]
final_data.append(dummy_row)

# SBA 컬럼 추가
df_all = pd.DataFrame(final_data, columns=columns)
df_all["SBA"] = df_all["SB"].astype(float) + df_all["CS"].astype(float)

# 저장
columns_with_sba = columns + ["SBA"]
df_all.to_csv("data/all_hitter_stats.csv", index=False, encoding="utf-8-sig", columns=columns_with_sba)
