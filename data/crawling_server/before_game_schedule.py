import csv
from datetime import datetime, timedelta
import subprocess

# 파일 경로 설정
CSV_PATH = "/home/ubuntu/baseball/data/kbo_schedule.csv"
SCRIPT_PATH = "/home/ubuntu/baseball/before_game.sh"
LOG_PATH = "/home/ubuntu/baseball/schedule_checker.log"
BEFORE_GAME_LOG = "/home/ubuntu/baseball/before_game.log"

# 현재 날짜 (형식: 2025.06.27)
now = datetime.now()
today_str = now.strftime("%Y.%m.%d")

# 로그 기록 함수
def log(message):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

log("스케줄 체크 시작")

# 스케줄 파일 읽기
with open(CSV_PATH, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # 오늘 날짜에 해당하는 경기 정보 찾기
        if len(row) >= 2 and row[0] == today_str:
            game_time_str = row[1]  # 경기 시작 시각 (HH:MM)
            datetime_str = today_str.replace('.', '-') + " " + game_time_str
            game_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

            # 경기 시작 50분 전으로 예약 시간 계산
            run_time = game_datetime - timedelta(minutes=50)
            run_time_str = run_time.strftime("%H:%M")

            # before_game.sh 스크립트를 예약 실행
            cmd = f'echo "sh \\"{SCRIPT_PATH}\\" >> \\"{BEFORE_GAME_LOG}\\" 2>&1" | at {run_time_str}'
            subprocess.run(cmd, shell=True)

            log(f"before_game.sh 예약됨: {run_time_str} (경기시간: {game_time_str})")
            break
    else:
        log(f"오늘 경기 없음 (날짜: {today_str})")
