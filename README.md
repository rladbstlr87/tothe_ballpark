# 1. 가상환경 활성화
- python -m venv venv
- source venv/Scripts/activate
- pip install django

# 2. git ignore 설정

# 3. startproject/ startapp
- `django-admin startproject baseball .`
- `django-admin startapp cal`
- pjt `settings.py`에 앱 등록하기

# 4. pjt 밖에 templates 폴더 생성
- `templates` 폴더 생성
- pjt `settings.py`에 `'DIRS': [BASE_DIR / 'templates'],` 등록하기

# 5. cal의 models.py 설정하기 


- `python manage.py makemigrations`
- `python manage.py migrate`

# createsuperuser
- 4team
- 1234 

# cal/utils.py



# 이전 달/ 다음 달 기능 구현 



- `templates/cal/calendar.html`
    - 버튼 추가 


- `static/style.css`
    - 버튼 꾸며주기

# 작업 순서

## 1. 데이터 수집/전처리
- `00 hitters_stats`
- `01 pitchers_stats`
- `02 구속`
- `03 도루`
- 타자보충에 있는 정보들을 `all_hitter_stats`에 추가
- `04 전처리`
- `05 스타일 추가`
- `06 kbo_schedule`
- `07 lineup`

## 2. DB 저장
- `hitters`
- `pitchers`
- `games`
- `lineup`