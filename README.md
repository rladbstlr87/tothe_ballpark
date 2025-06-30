
# 직돌이

최근 야구에 대한 관심이 높아지고 있지만, 직관을 가기 위해 필요한 정보가 부족한 경우가 많다. 특히 야구에 새로 입문한 팬들은 어떤 경기를 가야 하는지, 어떤 선수가 나오는지, 구장까지 어떻게 가야 하는지 등 다양한 정보를 일일이 찾아야 하는 번거로움이 있다. 직관 후에도 선수에 대한 이해 부족으로 인해 관람의 재미가 반감되기도 한다. 이런 점을 해결하기 위해 직관에 필요한 모든 정보를 한눈에 볼 수 있는 서비스를 기획하게 되었다.

---
## 데이터 처리 스크립트
- [데이터 수집 및 가공](https://github.com/dayofbaseball/KBO/tree/master/data/make_stat)
- [DB 저장 커맨드](https://github.com/dayofbaseball/KBO/tree/master/cal/management/commands)
- 스크립트 : `ready_develop.sh`, `before_game.sh`, `after_game.sh`
```bash

```
## 프로젝트 구조

- cal : 경기 일정 및 경기별 상세정보
- accounts : 계정 관리
- posts : 응원글 게시판
- jikdoltest : 유저의 직관 유형 테스트
- data : 데이터 수집/가공
- templates : base.html 기반 관리
- static : 공통 정적 파일 관리

---

## 사용자 기능

- 회원가입 / 로그인
- 아이디 / 비밀번호 찾기
- 마이페이지에서 정보 수정

---

## 경기 기능

### 경기 일정 캘린더

- 월별 달력에서 응원 팀 경기만 필터링
- 직관 여부 표시
- 경기결과 표시

### 경기 상세정보

- 선발 라인업 표시
- 직관 여부 버튼을 통해 유저 DB에 직관 여부 저장
- 선수별 자체 스탯 & 플레이 스타일 표기
- 경기 전이면 경기 예매 버튼 & 예매 가능일자 표시

### 구장 정보

- 구장 예매 링크
- 경기장까지의 길찾기 링크
- 경기장 좌석 추천 정보, 위치 이미지
- 주변 맛집, 주차장 정보 표시

---

## 응원글 게시판

- 게시글 CRUD (이미지 첨부 가능) & 좋아요 기능
- 댓글 CRUD (이미지 첨부 가능) & 좋아요 기능

---

## 순위

- KBO 순위
- 응원팀 기준 타자, 투수 순위

---

## 실행 방법

```bash
# 1. 가상환경 설정
python -m venv venv
source venv/Scripts/activate   # Mac/Linux는 source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 서버 실행
python manage.py runserver
```

---

## 기술 스택

- Python / Django
- SQLite3
- Selenium
- TailwindCSS
- HTML / JS

---

## 데이터 구성 및 전처리

- 경기 일정, 선발 라인업, 타자/투수 기록 등 전처리
- 데이터들을 Django Command로 DB 저장

---