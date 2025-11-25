from __future__ import annotations
from stat_def import TEAM_KBO

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
        driver.get(BASE_URL)
        # 시리즈 드롭다운을 정규시즌(0)으로 고정
        select_series_and_wait(driver, "0")

        for team in TEAM_KBO:
            # 팀 선택 및 테이블 로드 대기
            select_team_and_wait(driver, team)

            # 1페이지 선수 수집
            players = collect_players_on_page(driver)

            # 2페이지가 있으면 수집
            btn2 = driver.find_elements(By.XPATH, "//*[contains(@id,'ucPager')]//a[normalize-space()='2']")
            if btn2:
                btn2[0].click()
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(@id,'ucPager')]//a[normalize-space()='1']"))
                )
                players += collect_players_on_page(driver)
                # 1페이지 복귀
                driver.find_element(By.XPATH, "//*[contains(@id,'ucPager')]//a[normalize-space()='1']").click()

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
    df.to_csv("data/all_pitcher_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved rows: {len(df)} → data/all_pitcher_stats.csv")


if __name__ == "__main__":
    main()
