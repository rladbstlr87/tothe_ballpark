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

from crawling_pitcher_utils import (
    PITCHER_ORDER,
    collect_players_on_page,
    fetch_one_selenium,
    select_series_and_wait,
    select_team_and_wait,
)

BASE_URL = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx"
COLUMNS = ["team", "player_id", "player_name"] + PITCHER_ORDER


def main():
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
            # 매 팀마다 새로 로드해 1페이지 상태 보장
            driver.get(BASE_URL)
            # 시리즈 드롭다운을 정규시즌(0)으로 고정
            select_series_and_wait(driver, "0")

            # 팀 선택 및 테이블 로드 대기
            select_team_and_wait(driver, team)

            # 1페이지 선수 수집
            players = collect_players_on_page(driver)
            first_pid = players[0][0] if players else None

            # 2페이지가 있으면 수집
            btn2 = driver.find_elements(By.ID, "cphContents_cphContents_cphContents_ucPager_btnNo2")
            if not btn2:
                btn2 = driver.find_elements(By.XPATH, "//*[contains(@id,'ucPager')]//a[normalize-space()='2']")
            if btn2:
                btn2[0].click()
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
                        page2_players = []
                else:
                    page2_players = collect_players_on_page(driver)
                players += page2_players

            # 상세 파싱
            for pid, pname in players:
                data = fetch_one_selenium(driver, pid)
                if not data:
                    continue
                row = [team, pid, pname] + data
                final_rows.append(row)
                time.sleep(0.05)
    finally:
        driver.quit()

    df = pd.DataFrame(final_rows, columns=COLUMNS)
    data_dir = Path(__file__).resolve().parents[2] / "data" / "2026"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "all_pitcher_stats.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"saved rows: {len(df)} → {output_path}")


if __name__ == "__main__":
    main()
