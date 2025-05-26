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
first = True  # all_hitter_stats.csv 첫 저장 여부

for team in teams:
    print(f"\n▶ {team} 팀 데이터 수집 시작")
    page_dfs = []  # 각 페이지 데이터 저장

    # 팀 선택
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
    )
    select = Select(select_element)
    select.select_by_value(team)
    time.sleep(1)

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

        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent table"))
        )
        time.sleep(1)

        # HTML 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("#cphContents_cphContents_cphContents_udpContent table")

        # 헤더 추출
        headers = [th.get_text(strip=True) for th in table.select("thead th")]

        # 데이터 추출
        all_rows = []
        for row in table.select("tbody tr"):
            cells = [td.get_text(strip=True) for td in row.select("td")]
            if cells:
                all_rows.append(cells)

        df = pd.DataFrame(all_rows, columns=headers)
        page_dfs.append(df)

        # 2페이지 끝나면 1페이지로 다시 돌아가기
        if page_num == 2:
            driver.get("https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT")
            time.sleep(2)

    # 병합 및 저장
    if len(page_dfs) == 2:
        df1, df2 = page_dfs
        merge_keys = ['순위', '선수명', '팀명', 'AVG']
        combined_df = pd.merge(df1, df2.drop(columns=merge_keys), left_index=True, right_index=True)

        if '순위' in combined_df.columns:
            combined_df.drop(columns=['순위'], inplace=True)

        # 팀별 CSV 저장 제거됨
        # all_hitter_stats.csv에만 저장
        combined_df.to_csv("all_hitter_stats.csv", mode='w' if first else 'a', header=first, index=False, encoding='utf-8-sig')
        print(f"  ✔ all_hitter_stats.csv에 {team} 데이터 추가 완료")
        first = False
    else:
        print(f"  ⚠ {team} 팀의 데이터 수집 실패")

driver.quit()
