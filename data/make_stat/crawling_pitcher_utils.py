from __future__ import annotations

import time
from typing import List, Tuple, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

PITCHER_ORDER: List[str] = [
    "ERA", "G", "CG", "SHO", "W", "L", "SV", "HLD", "WPCT", "TBF", "NP", "IP",
    "H", "2B", "3B", "HR", "SAC", "SF", "BB", "IBB", "SO", "WP", "BK", "R",
    "ER", "BSV", "WHIP", "AVG", "QS",
]

DETAIL_URL = "https://www.koreabaseball.com/Record/Player/PitcherDetail/Basic.aspx?playerId={pid}"

def _wait_table_refresh(driver, timeout: int = 15) -> None:
    """테이블 tbody가 새로 그려질 때까지 staleness/존재 대기"""
    try:
        tbody = driver.find_element(
            By.CSS_SELECTOR,
            "#cphContents_cphContents_cphContents_udpContent div.record_result table tbody",
        )
        anchor = tbody.find_elements(By.TAG_NAME, "tr")[0] if tbody.find_elements(By.TAG_NAME, "tr") else tbody
        WebDriverWait(driver, timeout).until(EC.staleness_of(anchor))
    except Exception:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#cphContents_cphContents_cphContents_udpContent div.record_result table tbody tr")
            )
        )

def find_team_select(driver, timeout: int = 15):
    """팀 선택 드롭다운 요소를 여러 locator로 재시도하며 찾기"""
    locators = [
        (By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"),
        (By.CSS_SELECTOR, "select[id$='ddlTeam_ddlTeam']"),
        (By.XPATH, "//select[contains(@id,'ddlTeam_ddlTeam')]"),
        (By.XPATH, "//label[contains(normalize-space(.),'팀 선택')]/following::select[1]"),
    ]
    for by, value in locators:
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            continue
    raise TimeoutException("팀 선택 드롭다운을 찾지 못했습니다.")

def ensure_list_page(driver, base_url: str, timeout: int = 15):
    """목록 페이지가 아니면 base_url로 이동 후 팀 드롭다운 확보"""
    try:
        return find_team_select(driver, timeout=5)
    except TimeoutException:
        driver.get(base_url)
        return find_team_select(driver, timeout=timeout)

# ===== 투/타 공통 함수 =====
def select_series_and_wait(driver: webdriver.Chrome, series_value: str = "0", timeout: int = 15) -> None:
    """시리즈 드롭다운 선택 후 테이블 새로고침을 기다림"""
    sel = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (By.ID, "cphContents_cphContents_cphContents_ddlSeries_ddlSeries")
        )
    )
    Select(sel).select_by_value(series_value)
    _wait_table_refresh(driver, timeout=timeout)
    time.sleep(0.2)

def select_team_and_wait(driver, team_value: str, timeout: int = 15) -> None:
    """팀 드롭다운 선택 후 테이블 새로고침을 기다림"""
    sel = find_team_select(driver, timeout=timeout)
    Select(sel).select_by_value(team_value)
    _wait_table_refresh(driver, timeout=timeout)
    time.sleep(0.2)

def collect_players_on_page(driver) -> List[Tuple[str, str]]:
    """목록 테이블에서 (player_id, name)을 JS로 즉시 문자열화해 수집"""
    players = driver.execute_script(
        """
        return Array.from(
            document.querySelectorAll("#cphContents_cphContents_cphContents_udpContent div.record_result table tbody tr td:nth-child(2) a")
        ).map(a => ({href: a.href || "", name: (a.textContent || "").trim()}))
         .filter(p => p.href.includes("playerId=") && p.name);
        """
    ) or []
    out: List[Tuple[str, str]] = []
    for p in players:
        href = (p.get("href") or "").strip()
        name = (p.get("name") or "").strip()
        if href and name:
            pid = href.split("playerId=")[-1].strip()
            if pid:
                out.append((pid, name))
    return out

def fetch_one_selenium(driver, player_id: str, timeout: int = 15) -> Optional[list]:
    """투수 상세 페이지를 열어 요약/세부 테이블을 병합해 반환"""
    url = DETAIL_URL.format(pid=player_id)
    driver.get(url)
    try:
        table1 = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.tbl-type02.tbl-type02-pd0.mb35 > table > tbody")
            )
        )
        t1_cells = [td.text.strip() for td in table1.find_elements(By.CSS_SELECTOR, "td")]
        data1 = t1_cells[1:] if len(t1_cells) >= 2 else []

        data2 = []
        try:
            table2 = driver.find_element(By.CSS_SELECTOR, "div.player_records > div:nth-child(4) > table > tbody")
            data2 = [td.text.strip() for td in table2.find_elements(By.CSS_SELECTOR, "td")]
        except Exception:
            alt = driver.find_elements(By.CSS_SELECTOR, "div.player_records table tbody")
            if alt:
                data2 = [td.text.strip() for td in alt[0].find_elements(By.CSS_SELECTOR, "td")]

        merged = (data1 or []) + (data2 or [])
        return merged if len(merged) == len(PITCHER_ORDER) else None
    except (TimeoutException, StaleElementReferenceException):
        return None
    finally:
        # 목록 페이지로 복귀 (다음 선수/다음 팀을 위해 필수)
        try:
            driver.back()
        except Exception:
            pass
