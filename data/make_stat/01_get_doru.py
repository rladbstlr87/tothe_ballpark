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

df = pd.read_csv('../all_hitter_stats.csv')
df['선수명'] = df['선수명'].astype(str)
df['팀명'] = df['팀명'].astype(str)
df['G'] = df['G'].astype(str)

# 모든 팀 데이터를 저장할 리스트
all_team_dfs = []

for team in teams:
    print(f"\n▶ {team} 팀 데이터 수집 시작")

    # 팀 선택
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
    )
    select = Select(select_element)
    select.select_by_value(team)
    time.sleep(1)

    # 페이지 로딩 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent table"))
    )
    time.sleep(1)

    # HTML 파싱
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one(".tData01.tt")

    # 헤더 추출
    headers = [th.get_text(strip=True) for th in table.select("thead th")[1:]]
    # 데이터 추출
    all_rows = []
    for row in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in row.select("td")[1:]]
        if cells:
            all_rows.append(cells)
    df_doru = pd.DataFrame(all_rows, columns=headers)

    print(df_doru)
    # df과 병합할 데이터프레임에 추가
    all_team_dfs.append(df_doru)
    print(f"  ✔ {team} 데이터 수집 완료")

# 모든 팀 데이터 병합
if all_team_dfs:
    df_right = pd.concat(all_team_dfs, ignore_index=True)
    
    # 기존 컬럼들이 있다면 먼저 제거
    columns_to_update = ['SBA', 'SB', 'CS', 'SB%', 'OOB', 'PKO']
    existing_columns = [col for col in columns_to_update if col in df.columns]
    if existing_columns:
        df = df.drop(columns=existing_columns)
        print(f"기존 컬럼 제거: {existing_columns}")
    
    # df과 병합 (선수명, 팀명, G를 기준으로 새로운 데이터로 업데이트)
    df_merged = pd.merge(
        df, 
        df_right[['선수명', '팀명', 'G', 'SBA', 'SB', 'CS', 'SB%', 'OOB', 'PKO']], 
        left_on=['선수명', '팀명', 'G'], 
        right_on=['선수명', '팀명', 'G'], 
        how='left'
    )
    
    print(f"\n✔ df과 병합 완료 - 최종 데이터: {len(df_merged)}행")
    df_merged.to_csv("../all_hitter_stats.csv", index=False, encoding='utf-8-sig')
else:
    print("\n⚠ 수집된 데이터가 없습니다")
    df_merged = df

driver.quit()