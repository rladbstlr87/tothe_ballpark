from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# 크롬 드라이버 실행
driver = webdriver.Chrome()
driver.get("https://www.koreabaseball.com/Record/Player/Runner/Basic.aspx")

teams = ["LG", "HH", "LT", "SS", "SK", "NC", "OB", "HT", "KT", "WO"]
first = False  # all_hitter_stats.csv 첫 저장 여부

df_basic = pd.read_csv('../all_hitter_stats.csv')
df_basic['선수명'] = df_basic['선수명'].astype(str)
df_basic['팀명'] = df_basic['팀명'].astype(str)
df_basic['G'] = df_basic['G'].astype(str)

for team in teams:
    print(f"\n▶ {team} 팀 데이터 수집 시작")
    # 팀 선택
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
    )
    Select(select_element).select_by_value(team)
    time.sleep(1)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent table"))
    )
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one(".tData01.tt")

    # 헤더 및 데이터 추출. 0번째 인덱스는 '순위'인데 필요없어서 1번째부터 수집
    headers = [th.get_text(strip=True) for th in table.select("thead tr th")[1:]]
    rows = [
        [td.get_text(strip=True) for td in tr.select("td")[1:]]
        for tr in table.select("tbody tr")
    ]

    df_doru = pd.DataFrame(rows, columns=headers)
    df_doru['선수명'] = df_doru['선수명'].astype(str)
    df_doru['팀명'] = df_doru['팀명'].astype(str)
    df_doru['G'] = df_doru['G'].astype(str)

    # 병합
    merge_keys = ['선수명', '팀명', 'G']
    combined_df = pd.merge(df_basic, df_doru, on=merge_keys, how='left')

    combined_df.to_csv('../all_hitter_stats.csv', index=False, encoding='utf-8-sig')

    print(f"  ✔ all_hitter_stats.csv에 {team} 데이터 추가 완료")

driver.quit()
