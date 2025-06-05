
# ⚾ KBO 경기 정보 웹 애플리케이션

KBO 리그 팬들을 위한 웹 애플리케이션입니다. 사용자는 자신이 응원하는 팀의 경기 일정을 달력에서 확인하고, 선발 라인업과 기록, 경기장 정보, 커뮤니티 기능까지 함께 이용할 수 있습니다.

---

## 🧩 주요 기능 요약

- 사용자 맞춤 경기 일정 캘린더
- 경기별 선발 라인업 및 경기 기록
- 구장 상세 정보 (좌석도, 맛집, 주차장)
- 직관 경기 상세 정보 (유저의 직관 경기, 구장별 직관 승률, 모든 유저의 직관 승률 순위표)
- 게시판 및 댓글 시스템
- 크롤링 및 자동 DB 저장

---

## 📁 프로젝트 구조

```
KBO/
├── cal/            # 경기 캘린더, 기록, 라인업 등
├── accounts/       # 사용자 인증 및 팀 선택
├── posts/          # 게시판 및 댓글 기능
├── data/           # 기록 및 일정 CSV 데이터
├── templates/      # 전체 템플릿 폴더
├── static/         # 이미지, CSS, JS 등 정적 파일
├── manage.py
├── requirements.txt
├── README.md
```

---

## 👤 사용자 기능 (`accounts`)

- 회원가입 / 로그인 (응원팀 선택 포함)
- 사용자 프로필 기반 일정 필터링
- context processor로 팀 정보 템플릿에 전달

---

## 📅 경기 기능 (`cal`)

### 경기 일정 캘린더
- 월별 달력에서 내 팀 경기만 필터링
- 이전달/다음달 버튼으로 월 이동
- 직관 여부 표시

### 경기 상세정보
- 선발 라인업 표시
- 직관 여부 버튼을 통해 달력에 표시
- 각 타자/투수의 경기 기록
- 경기 점수 표시
- 경기 전이면 경기 예매 버튼

### 경기장 정보
- 경기장 좌석 정보, 위치 이미지
- 주변 맛집, 주차장 정보 표시
- 경기장까지의 길찾기 기능

### 데이터 자동화
- Selenium으로 KBO 웹사이트에서 일정/라인업/기록 수집
- CSV 파일로 저장 후 `manage.py` command로 DB 자동 저장

---

## 📝 게시판 기능 (`posts`)

- 게시글 작성, 수정, 삭제 (로그인 필요)
- 댓글 작성, 수정, 삭제 (이미지 포함 가능)
- 작성자만 수정/삭제 버튼 노출
- 게시글 목록, 상세 페이지 구현
- TailwindCSS 기반 반응형 UI

---

## ⚙️ 실행 방법

```bash
# 1. 가상환경 설정
python -m venv venv
source venv/Scripts/activate   # Mac/Linux는 source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. DB 마이그레이션 및 데이터 저장
./ready_develop.sh

# 4. 서버 실행
python manage.py runserver
```

---

## 🧠 기술 스택

- Python / Django
- SQLite3
- Selenium
- TailwindCSS
- HTML / JS / Jinja2 Template

---

## 🗂 데이터 구성 및 전처리

- 타자/투수 기록, 구속, 도루, 스타일 → 전처리 후 DB 저장
- 경기 일정, 선발 라인업 → Selenium 기반 크롤링
- CSV 파일을 Django Command로 DB 저장

---