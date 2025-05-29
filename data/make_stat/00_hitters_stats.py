from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# 크롬 드라이버 실행
driver = webdriver.Chrome()
driver.get("https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT")

teams = ["LG", "HH", "LT", "SS", "SK", "NC", "OB", "HT", "KT", "WO"]
first = True  # 첫 저장 여부

for team in teams:
    print(f"\n▶ {team} 팀 데이터 수집 시작")
    page_dfs = []

    # 팀 선택
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
    )
    select = Select(select_element)
    select.select_by_value(team)
    time.sleep(1)

    player_ids = {}

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent table"))
    )
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("#cphContents_cphContents_cphContents_udpContent table")

    for row in table.select("tbody tr"):
        link = row.select_one("td:nth-child(2) a")
        if link:
            player_name = link.get_text(strip=True)
            href = link.get("href", "")
            if "playerId=" in href:
                player_id = href.split("playerId=")[-1]
                player_ids[player_name] = player_id

    for page_num in [1, 2]:
        if page_num == 2:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent .more_record a.next"))
                )
                next_button.click()
                print("  - 2페이지 이동 중...")
                time.sleep(2)
            except Exception as e:
                print(f"  - 2페이지 이동 실패: {e}")
                break

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent table"))
        )
        time.sleep(1)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("#cphContents_cphContents_cphContents_udpContent table")

        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        rows = []
        for row in table.select("tbody tr"):
            cells = [td.get_text(strip=True) for td in row.select("td")]
            if cells:
                rows.append(cells)

        df = pd.DataFrame(rows, columns=headers)
        page_dfs.append(df)

        if page_num == 2:
            driver.get("https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT")
            time.sleep(2)

    if len(page_dfs) == 2:
        df1, df2 = page_dfs
        merge_keys = ['순위', '선수명', '팀명', 'AVG']
        combined_df = pd.merge(df1, df2.drop(columns=merge_keys), left_index=True, right_index=True)

        if '순위' in combined_df.columns:
            combined_df.drop(columns=['순위'], inplace=True)

        combined_df["player_id"] = combined_df["선수명"].map(player_ids).fillna("정보 없음")

        # ✅ 기존 '팀명' 컬럼에 두 글자 팀 코드로 덮어쓰기
        combined_df["팀명"] = team

        combined_df.to_csv("../all_hitter_stats.csv", mode='w' if first else 'a', header=first, index=False, encoding='utf-8-sig')
        print(f"  ✔ all_hitter_stats.csv에 {team} 데이터 추가 완료")
        first = False
    else:
        print(f"  ⚠ {team} 팀의 데이터 수집 실패")

driver.quit()
