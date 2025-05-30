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

# 기존 데이터 로드
df = pd.read_csv('../all_hitter_stats.csv')
df['선수명'] = df['선수명'].astype(str)
df['팀명'] = df['팀명'].astype(str)
df['G'] = df['G'].astype(str)

# 수집된 팀 데이터를 저장할 리스트
all_team_dfs = []

for team in teams:
    print(f"\n▶ {team} 팀 데이터 수집 시작")

    # 팀 선택
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
    )
    select = Select(select_element)
    select.select_by_value(team)
    time.sleep(2)

    # 테이블 로딩 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent table"))
    )
    time.sleep(2)

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
    df_doru["팀명"] = team  # '팀' → '팀명'으로 맞춤
    df_doru["G"] = df_doru["G"].astype(str)
    df_doru["선수명"] = df_doru["선수명"].astype(str)

    all_team_dfs.append(df_doru)
    print(f"  ✔ {team} 데이터 수집 완료")

# 크롬 종료
driver.quit()

# 병합
if all_team_dfs:
    df_right = pd.concat(all_team_dfs, ignore_index=True)

    # 병합 대상 컬럼
    columns_to_update = ['SBA', 'SB', 'CS', 'SB%', 'OOB', 'PKO']

    # 병합 키 타입 통일
    df_right['선수명'] = df_right['선수명'].astype(str)
    df_right['팀명'] = df_right['팀명'].astype(str)
    df_right['G'] = df_right['G'].astype(str)

    # 중복 제거
    df_right = df_right.drop_duplicates(subset=['선수명', '팀명', 'G'])

    # 기존 컬럼 제거
    existing_columns = [col for col in columns_to_update if col in df.columns]
    if existing_columns:
        df = df.drop(columns=existing_columns)
        print(f"기존 컬럼 제거: {existing_columns}")

    # 병합
    df_merged = pd.merge(
        df,
        df_right[['선수명', '팀명', 'G'] + columns_to_update],
        on=['선수명', '팀명', 'G'],
        how='left'
    )

    print(f"\n✔ 병합 완료: 총 {len(df_merged)}행, 도루 정보 추가된 선수 수: {df_merged['SBA'].notna().sum()}명")
    df_merged.to_csv("../all_hitter_stats.csv", index=False, encoding='utf-8-sig')
else:
    print("\n⚠ 수집된 데이터가 없습니다")
    df_merged = df
