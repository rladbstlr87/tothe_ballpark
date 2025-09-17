# 파일: kbo_hitter_utils.py
from __future__ import annotations

import re
from io import StringIO
from typing import Dict, List, Tuple

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


# ===== 상수 =====
TARGET_ORDER: List[str] = [
    "AVG", "G", "PA", "AB", "R", "H", "2B", "3B", "HR", "TB", "RBI",
    "SB", "CS", "SAC", "SF", "BB", "IBB", "HBP", "SO", "GDP",
    "SLG", "OBP", "E", "SB%", "MH", "OPS", "RISP", "PH-BA"
]

ALIAS: Dict[str, str] = {
    "타율": "AVG", "경기": "G", "타석": "PA", "타수": "AB", "득점": "R",
    "안타": "H", "2루타": "2B", "3루타": "3B", "홈런": "HR", "루타": "TB",
    "타점": "RBI", "도루": "SB", "도루사": "CS", "희생번트": "SAC",
    "희생플라이": "SF", "볼넷": "BB", "고의4구": "IBB", "사구": "HBP",
    "삼진": "SO", "병살타": "GDP", "장타율": "SLG", "출루율": "OBP",
    "실책": "E", "도루성공률": "SB%", "멀티히트": "MH", "OPS": "OPS",
    "득점권타율": "RISP", "대타타율": "PH-BA",
}


# ===== 파싱 유틸 =====
def _num_score(series: pd.Series) -> int:
    s = series.astype(str)
    return sum(bool(re.search(r"[0-9]", x)) for x in s)


def _canon_key(s: str) -> str:
    s = str(s).strip()
    m = re.search(r"\(([A-Z\-]+)\)", s)   # 장타율(SLG) → SLG
    if m:
        return m.group(1)
    s2 = re.sub(r"\(.*?\)", "", s).replace(" ", "").strip()
    return ALIAS.get(s2, s2)


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            " ".join([str(x) for x in tup if str(x) != "nan"]).strip()
            for tup in df.columns.values
        ]
    else:
        df.columns = [str(c).strip() for c in df.columns]
    # 1행 승격: 지표명이 다수 보이면 1행을 헤더로
    if len(df) > 0:
        first = [str(x).strip() for x in df.iloc[0].tolist()]
        score_keys = sum((_canon_key(x) in TARGET_ORDER) or (x in ALIAS) for x in first)
        if score_keys >= 3 and not any((_canon_key(c) in TARGET_ORDER) for c in df.columns):
            df.columns = first
            df = df.iloc[1:].reset_index(drop=True)
            df.columns = [str(c).strip() for c in df.columns]
    return df


def _pick_value_column(df: pd.DataFrame) -> int:
    """세로형 표에서 값 열 선택: 올해/최근연도 > 숫자 비율 높은 열"""
    cols = [str(c) for c in df.columns]
    years = [c for c in cols if re.fullmatch(r"20\d{2}", c)]
    if years:
        return cols.index(sorted(years)[-1])
    best_idx, best_score = 1, -1
    for j in range(1, df.shape[1]):
        score = _num_score(df.iloc[:, j])
        if score > best_score:
            best_idx, best_score = j, score
    return best_idx


def parse_hitter_detail(html: str) -> Dict[str, str] | None:
    """렌더된 표(여러 개일 수 있음)를 합쳐 TARGET_ORDER dict로 반환"""
    from pandas.errors import EmptyDataError
    all_dfs: List[pd.DataFrame] = []
    for kwargs in ({}, {"header": None}):
        try:
            all_dfs += pd.read_html(StringIO(html), **kwargs)
        except (ValueError, EmptyDataError):
            pass

    if not all_dfs:
        return None

    stats: Dict[str, str] = {}

    for raw in all_dfs:
        df = _normalize_df(raw)

        # 가로형: 컬럼=지표, 값=행 → 값이 많은 행 선택
        if df.shape[0] >= 1 and df.shape[1] >= 2:
            cols = [_canon_key(c) for c in df.columns]
            idxs = [i for i, k in enumerate(cols) if k in TARGET_ORDER]
            if idxs:
                sub = df.iloc[:, idxs]
                best_row_idx = sub.apply(_num_score, axis=1).idxmax()
                for i in idxs:
                    key = cols[i]
                    val = str(df.iloc[best_row_idx, i]).strip()
                    if key in TARGET_ORDER and val and key not in stats:
                        stats[key] = val

        # 세로형: 첫 열=지표, 값 열 자동 선택
        if df.shape[1] >= 2:
            kcol = df.iloc[:, 0].astype(str).str.strip()
            if sum((_canon_key(k) in TARGET_ORDER) for k in kcol) >= 3:
                vj = _pick_value_column(df)
                vcol = df.iloc[:, vj].astype(str).str.strip()
                for kk, vv in zip(kcol, vcol):
                    key = _canon_key(kk)
                    if key in TARGET_ORDER and vv and key not in stats:
                        stats[key] = vv

    return {k: stats.get(k, "") for k in TARGET_ORDER} if stats else None


# ===== Selenium 상세 페이지 파싱 =====
def fetch_one_selenium(driver: webdriver.Chrome, player_id: str) -> Dict[str, str] | None:
    """Selenium으로 상세를 새 탭에서 열고 파싱한 뒤 닫는다."""
    url = f"https://www.koreabaseball.com/Record/Player/HitterDetail/Basic.aspx?playerId={player_id}"

    base = driver.current_window_handle
    driver.execute_script("window.open('about:blank','_detail');")
    driver.switch_to.window(driver.window_handles[-1])

    try:
        driver.get(url)
        # 상세 블록 대기
        try:
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.player_records"))
            )
        except Exception:
            pass

        tables = driver.find_elements(By.CSS_SELECTOR, "div.player_records table")
        if tables:
            merged_html = "\n".join(t.get_attribute("outerHTML") for t in tables)
            data = parse_hitter_detail(merged_html)
        else:
            html = driver.page_source
            if "기록이 없습니다" in html:
                return None
            data = parse_hitter_detail(html)

        return data
    finally:
        try:
            driver.close()
        finally:
            if base in driver.window_handles:
                driver.switch_to.window(base)


# ===== 리스트 페이지 수집 =====
def collect_players_on_page(driver: webdriver.Chrome) -> List[Tuple[str, str]]:
    """현재 페이지의 (player_id, player_name) 목록을 JS로 즉시 문자열화하여 수집"""
    players = driver.execute_script(
        """
        return Array.from(
            document.querySelectorAll("a[href*='HitterDetail/Basic.aspx?playerId=']")
        ).map(a => ({href: a.href, name: a.textContent.trim()}))
         .filter(p => p.name);
        """
    )
    return [
        (p["href"].split("playerId=")[-1], p["name"])  # (id, name)
        for p in players
    ]


def select_team_and_wait(driver: webdriver.Chrome, team_code: str) -> None:
    """팀 드롭다운 재획득 → 선택 → staleness 대기 → 테이블 로드 대기"""
    sel = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//select[contains(@id,'ddlTeam')]"))
    )
    Select(sel).select_by_value(team_code)
    WebDriverWait(driver, 10).until(EC.staleness_of(sel))
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody"))
    )
