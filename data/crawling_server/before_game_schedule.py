import csv
from datetime import datetime, timedelta
import subprocess
import os

CSV_PATH = "/tothe_ballpark/data/kbo_schedule.csv"
SCRIPT_PATH = "/tothe_ballpark/data/crawling_server/before_game.sh"
LOG_PATH = "/tothe_ballpark/logs/schedule_checker.log"
BEFORE_GAME_LOG = "/tothe_ballpark/logs/before_game.log"

def log(message: str) -> None:
    now = datetime.now()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

now = datetime.now()
today_str = now.strftime("%Y.%m.%d")  # CSV 형식 예: 2025.06.27

log("스케줄 체크 시작")

if not os.path.exists(CSV_PATH):
    log(f"CSV 없음: {CSV_PATH}")
    raise SystemExit(0)

with open(CSV_PATH, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # [날짜, 시간, ...] 가정
        if len(row) >= 2 and row[0] == today_str:
            game_time_str = row[1]  # "HH:MM"
            # "YYYY-MM-DD HH:MM"
            dt_str = today_str.replace(".", "-") + " " + game_time_str
            game_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            run_time = game_dt - timedelta(minutes=50)
            run_time_str = run_time.strftime("%H:%M")

            # at 잡 등록 (before_game.sh -> 로그 남김)
            cmd = f'echo "sh \\"{SCRIPT_PATH}\\" >> \\"{BEFORE_GAME_LOG}\\" 2>&1" | at {run_time_str}'
            subprocess.run(cmd, shell=True)

            log(f"예약 완료: before_game.sh @ {run_time_str} (경기 {game_time_str})")
            break
    else:
        log(f"오늘 경기 없음: {today_str}")
