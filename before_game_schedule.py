import csv
from datetime import datetime, timedelta
import subprocess

CSV_PATH = "/mnt/c/Users/seong/KBO/data/kbo_schedule.csv"
SCRIPT_PATH = "/mnt/c/Users/seong/KBO/before_game.sh"
LOG_PATH = "/mnt/c/Users/seong/KBO/schedule_checker.log"
BEFORE_GAME_LOG = "/mnt/c/Users/seong/KBO/before_game.log"

now = datetime.now()
today_str = now.strftime("%Y.%m.%d")

def log(message):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

log("스케줄 체크 시작")

with open(CSV_PATH, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if len(row) >= 2 and row[0] == today_str:
            game_time_str = row[1]
            datetime_str = today_str.replace('.', '-') + " " + game_time_str
            game_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            run_time = game_datetime - timedelta(minutes=55)
            run_time_str = run_time.strftime("%H:%M")

            # at 명령어로 예약
            cmd = f'echo "sh \\"{SCRIPT_PATH}\\" >> \\"{BEFORE_GAME_LOG}\\" 2>&1" | at {run_time_str}'
            subprocess.run(cmd, shell=True)

            log(f"before_game.sh 예약됨: {run_time_str} (경기시간: {game_time_str})")
            break
    else:
        log(f"오늘 경기 없음 (날짜: {today_str})")


