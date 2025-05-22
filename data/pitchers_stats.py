from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from datetime import datetime

# IP 변환 함수
def convert_ip(ip_str):
    ip_str = ip_str.strip()
    if ' ' in ip_str:
        num, frac = ip_str.split()
        base = int(num)
        if frac == "1/3":
            return base + 0.3
        elif frac == "2/3":
            return base + 0.6
        else:
            return float(base)
    else:
        if ip_str == "1/3":
            return 0.3
        elif ip_str == "2/3":
            return 0.6
        else:
            try:
                return float(ip_str)
            except:
                return ip_str

# 크롬 드라이버 실행
driver = webdriver.Chrome()
url = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx"
driver.get(url)

teams = ["LG", "HH", "LT", "SS", "SK", "NC", "OB", "HT", "KT", "WO"]
first = True  # all_pitcher_stats.csv 첫 저장 여부

for team in teams:
    print(f"\n▶ {team} 팀 데이터 수집 시작")
    page_dfs = []
    player_birthdays = {}  # 선수명: 생일 저장용 딕셔너리
    wait = WebDriverWait(driver, 10)

    # 팀 선택
    select_element = wait.until(
        EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
    )
    select = Select(select_element)
    select.select_by_value(team)
    time.sleep(1)

    # 생일 정보 수집 (전체 선수 리스트에서 한 번만 크롤링)
    rows = driver.find_elements(By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent > div.record_result > table > tbody > tr")
    total_players = len(rows)

    for i in range(1, total_players + 1):
        try:
            player_link_selector = f"#cphContents_cphContents_cphContents_udpContent > div.record_result > table > tbody > tr:nth-child({i}) > td:nth-child(2) > a"
            player_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, player_link_selector)))
            player_name = player_link.text.strip()

            # playerId 추출
            player_id = player_link.get_attribute("href").split("playerId=")[-1]

            # requests로 프로필 페이지에서 생일 수집
            profile_url = f"https://www.koreabaseball.com/Record/Player/PitcherDetail/Basic.aspx?playerId={player_id}"
            res = requests.get(profile_url)
            soup = BeautifulSoup(res.content, "html.parser")
            birthday_tag = soup.select_one("#cphContents_cphContents_cphContents_playerProfile_lblBirthday")
            raw_birthday = birthday_tag.text.strip() if birthday_tag else ""

            # 날짜 포맷 통일: YYYY-MM-DD
            try:
                parsed = datetime.strptime(raw_birthday, "%Y년 %m월 %d일")
                birthday = parsed.strftime("%Y-%m-%d")
            except:
                birthday = "정보 없음"

            print(f"팀: {team} | 선수명: {player_name} | 생일: {birthday}")
            player_birthdays[player_name] = birthday

        except Exception as e:
            print(f"{team} 팀 {i}번째 선수 생일 크롤링 실패:", e)
            continue

    # 각 팀별 페이지(1,2)별 데이터 수집 및 병합
    for page_num in [1, 2]:
        if page_num == 2:
            try:
                next_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent .more_record a.next"))
                )
                next_button.click()
                print("  - 2페이지 이동 중...")
                time.sleep(2)
            except Exception as e:
                print(f"  - 2페이지 이동 실패: {e}")
                break

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent table"))
        )
        time.sleep(1)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("#cphContents_cphContents_cphContents_udpContent table")

        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        all_rows = []
        for row in table.select("tbody tr"):
            cells = [td.get_text(strip=True) for td in row.select("td")]
            if cells:
                all_rows.append(cells)

        df = pd.DataFrame(all_rows, columns=headers)

        # IP 컬럼이 있으면 변환 처리
        if 'IP' in df.columns:
            df['IP'] = df['IP'].apply(convert_ip)

        page_dfs.append(df)

        if page_num == 2:
            driver.get(url)
            time.sleep(2)
            # 팀 선택 초기화
            select_element = wait.until(
                EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
            )
            select = Select(select_element)
            select.select_by_value(team)
            time.sleep(2)

    if len(page_dfs) == 2:
        df1, df2 = page_dfs
        merge_keys = ['순위', '선수명', '팀명', 'ERA']
        combined_df = pd.merge(df1, df2.drop(columns=merge_keys), left_index=True, right_index=True)

        # 생일 컬럼 추가 (선수명 기준 매칭)
        combined_df['생일'] = combined_df['선수명'].map(player_birthdays).fillna("정보 없음")

        if '순위' in combined_df.columns:
            combined_df.drop(columns=['순위'], inplace=True)

        combined_df.to_csv("all_pitcher_stats.csv", mode='w' if first else 'a', header=first, index=False, encoding='utf-8-sig')
        print(f"  ✔ all_pitcher_stats.csv에 {team} 데이터 추가 완료")
        first = False
    else:
        print(f"  ⚠ {team} 팀의 데이터 수집 실패")

driver.quit()
print("\n✅ 모든 팀 데이터 수집 및 병합 완료")
