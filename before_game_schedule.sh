#!/bin/bash

CSV_PATH="/mnt/c/Users/seong/KBO/kbo_schedule.csv"
SCRIPT_PATH="/mnt/c/Users/seong/KBO/before_game.sh"
LOG_PATH="/mnt/c/Users/seong/KBO/schedule_checker.log"
BEFORE_GAME_LOG="/mnt/c/Users/seong/KBO/before_game.log"

# 오늘 날짜 포맷: 2025.06.24
TODAY=$(date '+%Y.%m.%d')

# 로그 시작
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 스케줄 체크 시작" >> "$LOG_PATH"

# 오늘 날짜에 해당하는 경기 시간 추출
GAME_TIME=$(awk -F',' -v date="$TODAY" '$1 == date {print $2; exit}' "$CSV_PATH")

if [ -z "$GAME_TIME" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 오늘 경기 없음 (날짜: $TODAY)" >> "$LOG_PATH"
    exit 0
fi

# 55분 전 시간 계산
# "2025.06.24 18:30" → "2025-06-24 18:30" 으로 변환 후 계산
DATETIME=$(echo "$TODAY $GAME_TIME" | sed 's/\./-/g')
RUN_TIME=$(date -d "$DATETIME - 55 minutes" '+%H:%M')

# 예약 실행
echo "sh \"$SCRIPT_PATH\" >> \"$BEFORE_GAME_LOG\" 2>&1" | at "$RUN_TIME"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] before_game.sh 예약됨: $RUN_TIME (경기시간: $GAME_TIME)" >> "$LOG_PATH"
