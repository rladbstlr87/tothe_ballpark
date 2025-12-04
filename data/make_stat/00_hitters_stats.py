# 파일: make_all_hitter_stats.py
from __future__ import annotations
from stat_def import TEAM_KBO
from pathlib import Path

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from crawling_hitter_utils import (
    HITTER_ORDER,
    collect_players_on_page,
    fetch_one_selenium,
    select_series_and_wait,
    select_team_and_wait,
)

BASE_URL = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT"
COLUMNS = ["team", "player_id", "player_name"] + HITTER_ORDER

def main():
    # Selenium 옵션
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=opts)
    final_rows = []

    try:
        for team in TEAM_KBO:
            # 매 팀마다 페이지를 새로 열어 1페이지 상태로 리셋
            driver.get(BASE_URL)
            # 새로 추가된 시리즈 필터는 기본값(0)으로 고정
            select_series_and_wait(driver, "0")

            # 팀 선택 및 대기
            select_team_and_wait(driver, team)

            # 1페이지 선수 수집
            players = collect_players_on_page(driver)
            first_pid = players[0][0] if players else None

            # 2페이지 있으면 수집
            btn2 = driver.find_elements(By.ID, "cphContents_cphContents_cphContents_ucPager_btnNo2")
            if not btn2:
                btn2 = driver.find_elements(By.XPATH, "//*[contains(@id,'ucPager')]//a[normalize-space()='2']")
            if btn2:
                btn2[0].click()
                # 페이지가 실제로 넘어갔는지(첫 선수 id가 달라질 때까지) 기다린다
                page2_players = []
                if first_pid:
                    try:
                        WebDriverWait(driver, 5).until(
                            lambda d: (
                                collect_players_on_page(d)
                                and collect_players_on_page(d)[0][0] != first_pid
                            )
                        )
                        page2_players = collect_players_on_page(driver)
                    except TimeoutException:
                        # 2페이지 버튼이 비활성/없음 등으로 실제 전환이 안 되는 경우
                        page2_players = []
                else:
                    page2_players = collect_players_on_page(driver)
                players += page2_players

            # 상세 파싱
            for pid, pname in players:
                data = fetch_one_selenium(driver, pid)
                if not data:
                    continue  # 기록 없음/파싱 실패는 건너뜀

                row = [team, pid, pname] + [data.get(k, "") for k in HITTER_ORDER]
                final_rows.append(row)

                # 과도한 요청 방지
                time.sleep(0.05)

    finally:
        driver.quit()

    # DataFrame 구성 및 SBA 계산
    df = pd.DataFrame(final_rows, columns=COLUMNS)
    # 숫자 변환 후 NaN→0 처리
    for col in ["SB", "CS"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
    df["SBA"] = df["SB"] + df["CS"]

    out_cols = COLUMNS + ["SBA"]
    data_dir = Path(__file__).resolve().parents[2] / "data" / "2026"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "all_hitter_stats.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig", columns=out_cols)
    print(f"saved rows: {len(df)} → {output_path}")

if __name__ == "__main__":
    main()
