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
``` python
class Game(models.Model):
    date = models.DateField()
    time = models.TimeField()
    away_team = models.CharField(max_length = 100)
    home_team = models.CharField(max_length = 100)
    stadium = models.CharField(max_length = 100)
    def __str__(self):
        return f"{self.away_team} vs {self.away_team} on {self.date}"
```
- `python manage.py makemigrations`
- `python manage.py migrate`

# createsuperuser
- 4team
- 1234 

# cal/utils.py
```python
from datetime import datetime, timedelta # 날짜와 시간 처리를 위한 모듈
from calendar import HTMLCalendar # 모듈에서 제공하는 html 형식의 캘린더를 생성하는 클래스
from .models import Game # 현재 모델에서 불러온 클래스 

class Calendar(HTMLCalendar): # calemdar 클래스는 htmlcalendar를 상속받아 특정 연도와 월을 받아 캘린더를 생성하도록함
    def __init__(self, year = None, month=None): # __init__ 메서드에서 year와 month를 받아서 인스턴스 변수로 저장
        self.year = year
        self.month = month
        super(Calendar, self).__init__()
    
    def formatday(self, day, games): # day 현재 날짜, contents : 현재 달의 모든 일정 데이터 
        games_per_day = games.filter(start_time__day = day) # 현재 날짜에 해당하는 일정만 필터링링
        d = ''
        for game in games_per_day: # 필터링된 일정들을 event로 순회하면서 html 리스트 아이템(li)로 만들어서 d에 추가 
            d += f'<li> {game.away_team} vs {game.home_team} at {game.stadium} </li> ' 

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'
    
    def formatweek(self, theweek, games):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, games)
        return f'<tr> {week} </tr>'
    
    def formatmonth(self, withyear = True):
        games = Game.objects.filter(date__year = self.year, date__month=self.month)
        cal = f'<table border=\"0\" cellpadding=\"0\" cellspacing=\"0\" class=\"calendar\">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, games)}\n'
        return cal
```

# 이전 달/ 다음 달 기능 구현 



- `templates/cal/calendar.html`
    - 버튼 추가 


- `static/style.css`
    - 버튼 꾸며주기


# 구단별 kbo 일정 크롤링한거 집어넣기 
- 일단 한화만 해보기
1. 폴더랑 파일 생성 
cal/
  management/
    __init__.py
    commands/
      __init__.py
      import_hanwha.py 