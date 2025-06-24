#!/bin/bash

CSV_PATH="/mnt/c/Users/seong/KBO/kbo_schedule.csv"
SCRIPT_PATH="/mnt/c/Users/seong/KBO/before_game.sh"
LOG_PATH="/mnt/c/Users/seong/KBO/schedule_checker.log"
BEFORE_GAME_LOG="/mnt/c/Users/seong/KBO/before_game.log"

TODAY=$(date '+%Y.%m.%d')

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 스케줄 체크 시작" >> "$LOG_PATH"

# 오늘 날짜에 해당하는 첫 줄을 가져오고 BOM 및 \r 제거
LINE=$(grep "^$TODAY," "$CSV_PATH" | head -n 1 | tr -d '\r' | sed 's/^\xEF\xBB\xBF//')

# 시간 추출
GAME_TIME=$(echo "$LINE" | cut -d',' -f2)

if [ -z "$GAME_TIME" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 오늘 경기 없음 (날짜: $TODAY)" >> "$LOG_PATH"
    exit 0
fi

# 시간 계산
DATETIME=$(echo "$TODAY $GAME_TIME" | sed 's/\./-/g')
RUN_TIME=$(date -d "$DATETIME - 55 minutes" '+%H:%M')

# 예약
echo "sh \"$SCRIPT_PATH\" >> \"$BEFORE_GAME_LOG\" 2>&1" | at "$RUN_TIME"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] before_game.sh 예약됨: $RUN_TIME (경기시간: $GAME_TIME)" >> "$LOG_PATH"
