import os
import time
import re
import calendar
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)


def extract_team_code(img_url: str) -> str:
    filename = img_url.split("/")[-1]
    return filename.split(".")[0]


def _clean_text(text: str) -> str:
    parts = text.splitlines()
    return parts[-1].strip() if parts else ""


def parse_group(group, target_day: str, seen: set, results: list):
    """Return (matched_day, has_rows)"""
    date_pattern = re.compile(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일")
    header_lines = group.text.splitlines()
    if not header_lines:
        return False, False
    m = date_pattern.search(header_lines[0])
    if not m:
        return False, False
    month = int(m.group(1))
    day = int(m.group(2))
    group_day = f"{target_day[:4]}.{month:02d}.{day:02d}"
    if group_day != target_day:
        return False, False

    # 해당 날짜 섹션이 뷰포트에 들어오도록 스크롤 후 자식 li 로드 기다리기
    try:
        group.location_once_scrolled_into_view
        driver.execute_script("arguments[0].scrollIntoView(true);", group)
        time.sleep(0.3)
        WebDriverWait(driver, 3).until(
            lambda d: len(group.find_elements(By.CSS_SELECTOR, "li[class*='MatchBox_match_item__']")) > 0
        )
    except Exception:
        pass

    lis = group.find_elements(By.CSS_SELECTOR, "li[class*='MatchBox_match_item__']")
    if not lis:
        return True, False

    has_rows = False
    for li in lis:
        try:
            time_raw = li.find_element(By.CSS_SELECTOR, 'div[class*="MatchBox_time__"]').text.strip()
            time_text = _clean_text(time_raw)
        except Exception:
            time_text = ""

        try:
            stadium_raw = li.find_element(By.CSS_SELECTOR, 'div[class*="MatchBox_stadium__"]').text.strip()
            stadium = _clean_text(stadium_raw)
        except Exception:
            stadium = ""

        try:
            status = li.find_element(By.CSS_SELECTOR, 'em[class*="MatchBox_status__"]').text.strip()
        except Exception:
            status = ""

        teams = li.find_elements(By.CSS_SELECTOR, 'div[class*="MatchBoxHeadToHeadArea_team_item__"]')
        if len(teams) != 2:
            continue

        t1_block, t2_block = teams

        try:
            t1_img = t1_block.find_element(By.TAG_NAME, "img").get_attribute("src")
            t1_code = extract_team_code(t1_img)
        except Exception:
            continue
        try:
            t1_score = t1_block.find_element(By.CSS_SELECTOR, '[class*="MatchBoxHeadToHeadArea_score__"]').text.strip()
        except Exception:
            t1_score = ""
        t1_result = ""
        for sp in t1_block.find_elements(By.TAG_NAME, "span"):
            if sp.text in ["승", "패", "무"]:
                t1_result = sp.text
                break

        try:
            t2_img = t2_block.find_element(By.TAG_NAME, "img").get_attribute("src")
            t2_code = extract_team_code(t2_img)
        except Exception:
            continue
        try:
            t2_score = t2_block.find_element(By.CSS_SELECTOR, '[class*="MatchBoxHeadToHeadArea_score__"]').text.strip()
        except Exception:
            t2_score = ""
        t2_result = ""
        for sp in t2_block.find_elements(By.TAG_NAME, "span"):
            if sp.text in ["승", "패", "무"]:
                t2_result = sp.text
                break

        note = "-"
        if status in ["취소", "우천취소"]:
            note = status

        key = (
            group_day,
            time_text,
            t1_code,
            t2_code,
            t1_score,
            t2_score,
            t1_result,
            t2_result,
            stadium,
            note,
        )
        if key in seen:
            continue
        seen.add(key)
        has_rows = True

        results.append(
            {
                "day": group_day,
                "time": time_text,
                "team1": t1_code,
                "team1_score": t1_score,
                "team1_result": t1_result,
                "team2": t2_code,
                "team2_score": t2_score,
                "team2_result": t2_result,
                "stadium": stadium,
                "note": note,
            }
        )

    return True, has_rows


def fetch_day(target_day: str):
    """target_day: YYYY.MM.DD"""
    results = []
    seen = set()
    target_dash = target_day.replace(".", "-")
    url = f"https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date={target_dash}"

    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='ScheduleLeagueType_match_list_group__']"))
        )
    except TimeoutException:
        return results, False

    matched_header = False
    matched_rows = False
    for _ in range(50):
        groups = driver.find_elements(By.CSS_SELECTOR, "div[class*='ScheduleLeagueType_match_list_group__']")
        for group in groups:
            g_matched, has_rows = parse_group(group, target_day, seen, results)
            matched_header = matched_header or g_matched
            matched_rows = matched_rows or has_rows
        if matched_rows:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.8)

    return results, matched_header or matched_rows


def crawl_kbo_schedule(year=2026):
    data_dir = Path(__file__).resolve().parents[2] / "data" / "2026"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "kbo_schedule.csv"

    if os.path.exists(output_path):
        os.remove(output_path)

    all_rows = []

    for month in range(3, 11):
        last_day = calendar.monthrange(year, month)[1]
        start_day = 8 if month == 3 else 1
        for day in range(start_day, last_day + 1):
            day_str = f"{year}.{month:02d}.{day:02d}"
            rows, matched = fetch_day(day_str)
            if matched:
                if rows:
                    all_rows.extend(rows)
                    df = pd.DataFrame(rows)
                    write_header = not os.path.exists(output_path) or os.path.getsize(output_path) == 0
                    df.to_csv(
                        output_path,
                        mode="a",
                        index=False,
                        encoding="utf-8-sig",
                        header=write_header,
                    )
                else:
                    print(f"[INFO] {day_str} 경기 없음")
            else:
                print(f"[WARN] {day_str} 수집 실패 (헤더 미매칭)")

    driver.quit()
    return pd.DataFrame(all_rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KBO schedule crawler (naver mobile)")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--date")
    args = parser.parse_args()

    data_dir = Path(__file__).resolve().parents[2] / "data" / "2026"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "kbo_schedule.csv"

    if args.date:
        target = args.date
        if "." in target:
            target = target.replace(".", "-")
        rows, matched = fetch_day(target.replace("-", "."))
        if matched and rows:
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(df)
            print(f"[INFO] saved {output_path} rows={len(rows)}")
        elif matched:
            print(f"[INFO] {target} ?? ??? ??")
        else:
            print(f"[WARN] {target} ???? ?? ?????.")
        driver.quit()
    else:
        df = crawl_kbo_schedule(args.year)
        print(df)
