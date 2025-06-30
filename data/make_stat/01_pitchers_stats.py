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

base_url = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx"
detail_url = "https://www.koreabaseball.com/Record/Player/PitcherDetail/Basic.aspx?playerId={}"

final_data = []

columns = [
    "team", "player_id", "player_name",
    "ERA", "G", "CG", "SHO", "W", "L", "SV", "HLD", "WPCT", "TBF", "NP", "IP", "H", "2B", "3B", "HR",
    "SAC", "SF", "BB", "IBB", "SO", "WP", "BK", "R", "ER", "BSV", "WHIP", "AVG", "QS"
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

    # 팀별 데이터 저장 리스트
    team_data = []

    # 각 선수 상세 페이지 접속 및 데이터 수집
    for player_id, player_name in player_infos:
        url = detail_url.format(player_id)
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")

        # 첫 번째 테이블 (요약 정보, 팀명 제외)
        try:
            table1 = soup.select_one("div.tbl-type02.tbl-type02-pd0.mb35 > table > tbody")
            data1 = [td.text.strip() for td in table1.select("td")][1:]
        except:
            data1 = []

        # 두 번째 테이블 (세부 성적)
        try:
            table2 = soup.select_one("div.player_records > div:nth-child(4) > table > tbody")
            data2 = [td.text.strip() for td in table2.select("td")]
        except:
            data2 = []

        # 두 테이블 모두 있는 경우에만 저장
        if data1 and data2:
            row = [team, player_id, player_name] + data1 + data2
            team_data.append(row)

        time.sleep(0.3)

    # 팀 데이터 누적
    final_data.extend(team_data)

    # 중간 저장
    df_all = pd.DataFrame(final_data, columns=columns)
    df_all.to_csv("data/all_pitcher_stats.csv", index=False, encoding="utf-8-sig")

# 드라이버 종료
driver.quit()

# 임시 선수 추가
dummy_row = [
    "TMP", "1", "임시선수",
    "3.21", 10, 0, 0, 2, 1, 1, 0, "0.667", 150, 1000, 55.1, 48, 5, 0, 3,
    2, 1, 12, 1, 35, 1, 0, 15, 12, 0, "1.25", "0.220", 2
]
final_data.append(dummy_row)

# 최종 저장
df_all = pd.DataFrame(final_data, columns=columns)
df_all.to_csv("data/all_pitcher_stats.csv", index=False, encoding="utf-8-sig")
