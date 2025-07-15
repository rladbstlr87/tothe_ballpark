import csv
from datetime import datetime, timedelta
import subprocess

# 파일 경로 설정
CSV_PATH = "/Users/m2/Desktop/tothe_ballpark/data/kbo_schedule.csv"
SCRIPT_PATH = "/Users/m2/Desktop/tothe_ballpark/data/crawling_local/before_game.sh"
LOG_PATH = "/Users/m2/Desktop/tothe_ballpark/data/schedule_checker.log"
BEFORE_GAME_LOG = "/Users/m2/Desktop/tothe_ballpark/data/before_game.log"

# 현재 시간
now = datetime.now()
today_str = now.strftime("%Y.%m.%d")

# 로그 기록 함수
def log(message):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

log("스케줄 체크 시작")

# CSV 파일 열어서 오늘 날짜에 해당하는 경기 찾기
with open(CSV_PATH, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if len(row) >= 2 and row[0] == today_str:
            game_time_str = row[1]  # 경기 시간 문자열
            datetime_str = today_str.replace('.', '-') + " " + game_time_str
            game_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

            # 경기 시작 55분 전 시간 계산
            run_time = game_datetime - timedelta(minutes=55)
            run_time_str = run_time.strftime("%H:%M")

            # at 명령어로 스크립트 예약 실행
            cmd = f'echo "sh \\"{SCRIPT_PATH}\\" >> \\"{BEFORE_GAME_LOG}\\" 2>&1" | at {run_time_str}'
            subprocess.run(cmd, shell=True)

            log(f"before_game.sh 예약됨: {run_time_str} (경기시간: {game_time_str})")
            break
    else:
        log(f"오늘 경기 없음 (날짜: {today_str})")
