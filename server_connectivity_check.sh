#!/usr/bin/env bash
# server_connectivity_check.sh — "접속" 우선 점검/복구 (비-systemd, Nginx 8081/8443, Gunicorn 127.0.0.1:8000)
# ⚠️ 원격 외부망 없이 동작. git pull, 패키지 설치, 마이그레이션 등은 수행하지 않음.
#
# 사용법 예시:
#   ./server_connectivity_check.sh </절대경로/프로젝트> [도메인] [포트8443]
# 실제 명령어:
#   ./server_connectivity_check.sh /root/tothe_ballpark totheballpark.info 8443
#
# 환경변수(옵션):
#   VENV_CANDIDATES="프로젝트내_venv경로1,경로2,..."  (기본: venv-310, venv-py310, venv, .venv 순)
#   TRY_RESTART=auto|yes|no    (기본 auto: 꺼져있으면 시작, 살아있으면 건드리지 않음)
#   FALLBACK_RUNSERVER=no|yes  (기본 no: gunicorn 실패 시에만 임시 runserver 0.0.0.0:8000 기동)
#   WSGI_MODULE=패키지.wsgi:application (기본: baseball.wsgi:application 또는 repo에서 자동 탐색)
#   NGINX_TEST_ONLY=yes|no     (기본 no: nginx -t 통과하고 비활성/미기동이면 시작/재시작 수행)
#
set -Eeuo pipefail

PROJECT_DIR="${1:-}"
DOMAIN="${2:-totheballpark.info}"
HTTPS_PORT="${3:-8443}"

if [[ -z "${PROJECT_DIR}" ]]; then
  echo "사용법: $0 </절대경로/프로젝트> [도메인] [포트8443]" >&2
  exit 2
fi
if [[ ! -d "${PROJECT_DIR}" ]]; then
  echo "에러: 디렉토리가 존재하지 않습니다: ${PROJECT_DIR}" >&2
  exit 2
fi

TRY_RESTART="${TRY_RESTART:-auto}"
FALLBACK_RUNSERVER="${FALLBACK_RUNSERVER:-no}"
NGINX_TEST_ONLY="${NGINX_TEST_ONLY:-no}"

VENV_CANDIDATES_DEFAULT="${PROJECT_DIR}/venv-310,${PROJECT_DIR}/venv-py310,${PROJECT_DIR}/venv,${PROJECT_DIR}/.venv"
VENV_CANDIDATES="${VENV_CANDIDATES:-$VENV_CANDIDATES_DEFAULT}"

REPORT="${PROJECT_DIR}/connectivity_report.txt"
: > "${REPORT}"

log(){ printf "[%s] %s\n" "$(date +'%F %T')" "$*"; }
warn(){ printf "[%s] [경고] %s\n" "$(date +'%F %T')" "$*" >&2; }
fail(){ printf "[%s] [실패] %s\n" "$(date +'%F %T')" "$*" >&2; exit 1; }
section(){ echo -e "\n==== $* ====" | tee -a "${REPORT}"; }

cd "${PROJECT_DIR}"

section "1) Python/가상환경 (이름 변경/생성 안 함 — 존재하는 것만 사용)"
# venv 후보 중 첫 번째 존재 경로 선택
IFS=',' read -r -a VLIST <<< "${VENV_CANDIDATES}"
VENV_DIR=""
for v in "${VLIST[@]}"; do
  if [[ -x "${v}/bin/python" ]]; then VENV_DIR="${v}"; break; fi
done

if [[ -z "${VENV_DIR}" ]]; then
  warn "가상환경을 찾지 못했습니다. (시도: ${VENV_CANDIDATES}) — 시스템 python으로 진행합니다."
  PYTHON_BIN="$(command -v python3 || true)"
  PIP_BIN="$(command -v pip3 || true)"
  GUNICORN_BIN="$(command -v gunicorn || true)"
else
  echo "발견된 venv: ${VENV_DIR}" | tee -a "${REPORT}"
  PYTHON_BIN="${VENV_DIR}/bin/python"
  PIP_BIN="${VENV_DIR}/bin/pip"
  GUNICORN_BIN="${VENV_DIR}/bin/gunicorn"
fi

if [[ -z "${PYTHON_BIN}" ]]; then fail "python3 실행 파일을 찾지 못했습니다."; fi
echo "python 경로: ${PYTHON_BIN}" | tee -a "${REPORT}"
"${PYTHON_BIN}" -V | tee -a "${REPORT}" || true

section "2) Django 경로/WSGI 모듈 추정"
WSGI_MODULE="${WSGI_MODULE:-}"
if [[ -z "${WSGI_MODULE}" ]]; then
  if [[ -f "${PROJECT_DIR}/baseball/wsgi.py" ]]; then
    WSGI_MODULE="baseball.wsgi:application"
  else
    # 레포 내 임의의 wsgi.py 탐색 (1개만 허용)
    mapfile -t CAND < <(find "${PROJECT_DIR}" -maxdepth 3 -type f -name wsgi.py | sed "s#${PROJECT_DIR}/##")
    if (( ${#CAND[@]} == 1 )); then
      PKG="$(dirname "${CAND[0]}")"
      PKG="${PKG//\//.}"
      WSGI_MODULE="${PKG}.wsgi:application"
    fi
  fi
fi
echo "WSGI_MODULE=${WSGI_MODULE:-'(미확정: runserver 대체 가능)'}" | tee -a "${REPORT}"

section "3) Gunicorn 프로세스/포트 확인"
BIND_ADDR="127.0.0.1:8000"
if command -v ss >/dev/null 2>&1; then
  ss -ltnp | tee -a "${REPORT}" || true
elif command -v lsof >/dev/null 2>&1; then
  lsof -nP -iTCP -sTCP:LISTEN | tee -a "${REPORT}" || true
fi

is_listen_8000="no"
if ss -ltn 2>/dev/null | grep -q ":8000\\b"; then is_listen_8000="yes"; fi

if [[ "${is_listen_8000}" == "no" ]]; then
  echo "127.0.0.1:8000 리스닝 없음 → TRY_RESTART=${TRY_RESTART}" | tee -a "${REPORT}"
  if [[ "${TRY_RESTART}" != "no" ]]; then
    if [[ -n "${GUNICORN_BIN}" && -n "${WSGI_MODULE}" ]]; then
      log "gunicorn 기동 시도: ${GUNICORN_BIN} -b ${BIND_ADDR} ${WSGI_MODULE}"
      set +e
      (nohup "${GUNICORN_BIN}" -b "${BIND_ADDR}" "${WSGI_MODULE}" --workers 2 --timeout 60 >/tmp/gunicorn.out 2>&1 &)
      sleep 2
      set -e
      if ss -ltn 2>/dev/null | grep -q ":8000\\b"; then
        log "gunicorn 기동 성공"
      else
        warn "gunicorn 기동 실패"
        if [[ "${FALLBACK_RUNSERVER}" == "yes" ]]; then
          log "임시 대체: runserver 0.0.0.0:8000 기동 시도 (테스트용)"
          set +e
          (nohup "${PYTHON_BIN}" manage.py runserver 0.0.0.0:8000 >/tmp/runserver.out 2>&1 &)
          sleep 2
          set -e
        fi
      fi
    else
      warn "gunicorn 실행 파일 또는 WSGI 모듈이 없어 기동을 생략합니다."
    fi
  fi
else
  echo "127.0.0.1:8000 이미 리스닝 중 — 재시작하지 않음(TRY_RESTART=${TRY_RESTART})" | tee -a "${REPORT}"
fi

section "4) Nginx 구성/상태 확인 (8081/8443)"
if command -v nginx >/dev/null 2>&1; then
  echo "- nginx -t (구문 검사)" | tee -a "${REPORT}"
  if ! nginx -t >> "${REPORT}" 2>&1; then
    warn "nginx 설정 오류 — 상세는 report 참고"; 
  else
    echo "nginx -t OK" | tee -a "${REPORT}"
    # 동작 여부
    if pgrep -x nginx >/dev/null 2>&1; then
      echo "nginx 프로세스: 실행 중" | tee -a "${REPORT}"
      if [[ "${NGINX_TEST_ONLY}" == "no" ]]; then
        log "nginx graceful reload"
        nginx -s reload || warn "nginx reload 실패"
      fi
    else
      echo "nginx 프로세스: 미실행" | tee -a "${REPORT}"
      if [[ "${NGINX_TEST_ONLY}" == "no" ]]; then
        log "nginx 시작 시도"
        nginx || warn "nginx 시작 실패"
      fi
    fi
  fi
else
  warn "nginx 명령을 찾지 못했습니다."
fi

section "5) 포트 8081 / 8443 리스닝 확인"
if command -v ss >/dev/null 2>&1; then
  SS="$(ss -ltnp || true)"
  echo "${SS}" | tee -a "${REPORT}"
  echo "${SS}" | grep -E ":(8081|${HTTPS_PORT})\\b" || warn "8081/8443 리스너가 감지되지 않습니다."
fi

section "6) 내부 루프백 헬스체크"
if command -v curl >/dev/null 2>&1; then
  echo "- curl -k --resolve ${DOMAIN}:${HTTPS_PORT}:127.0.0.1 https://${DOMAIN}:${HTTPS_PORT}/ -I" | tee -a "${REPORT}"
  curl -sS -k --max-time 5 --resolve "${DOMAIN}:${HTTPS_PORT}:127.0.0.1" "https://${DOMAIN}:${HTTPS_PORT}/" -I | tee -a "${REPORT}" || true
  echo "- curl http://127.0.0.1:8081/ -I" | tee -a "${REPORT}"
  curl -sS --max-time 3 "http://127.0.0.1:8081/" -I | tee -a "${REPORT}" || true
else
  warn "curl 미설치 — HTTP 헬스체크 생략"
fi

section "7) ALLOWED_HOSTS/호스트 헤더 문제 감지 (선택)"
# Django에 직접 붙어 400 Bad Request 가 나오는지 단서만 확인
if command -v curl >/dev/null 2>&1; then
  echo "- gunicorn 직접 헬스체크 (Host 헤더 도메인 고정)" | tee -a "${REPORT}"
  curl -sS --max-time 3 -H "Host: ${DOMAIN}" "http://127.0.0.1:8000/" -I | tee -a "${REPORT}" || true
fi

section "8) 요약"
echo "프로젝트: ${PROJECT_DIR}" | tee -a "${REPORT}"
echo "venv 사용: ${VENV_DIR:-'(미탐지 — 시스템 python)'}" | tee -a "${REPORT}"
echo "WSGI: ${WSGI_MODULE:-'(미확정)'}" | tee -a "${REPORT}"
echo "도메인: ${DOMAIN}, HTTPS 포트: ${HTTPS_PORT}" | tee -a "${REPORT}"
echo "리포트: ${REPORT}" | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"
echo "다음 단계 권장:" | tee -a "${REPORT}"
echo " - Nginx 8443 리스너 OK & 127.0.0.1:8000 응답 OK ⇒ 외부 접속은 라우터 포워딩(443→${HTTPS_PORT})만 확인" | tee -a "${REPORT}"
echo " - 응답이 400 Bad Request (Invalid Host header) ⇒ 서버 코드의 ALLOWED_HOSTS 또는 prod 설정 적용 필요" | tee -a "${REPORT}"
echo " - gunicorn 미기동 시: TRY_RESTART=auto(기본)로 자동 기동 시도, 실패하면 로그(/tmp/gunicorn.out) 확인" | tee -a "${REPORT}"

log "접속 점검 스크립트 완료"