from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta, date
from django.utils.safestring import mark_safe
import calendar
from .models import *
from .utils import Calendar

# 메인 페이지
def index(request):
    return render(request, 'index.html')

# 함수형 뷰로 calendar 페이지 구현
def calendar_view(request):
    d = get_date(request.GET.get('day', None))
    cal = Calendar(d.year, d.month)
    html_cal = cal.formatmonth(withyear=True)
    context = {
        'calendar': mark_safe(html_cal),
        'prev_month': prev_month(d),
        'next_month': next_month(d),
        # 필요하다면 추가 context
    }
    if request.user.is_authenticated:
        user_team = request.user.team
    print(f'[DEBUG] user_team={user_team}')

    
    return render(request, 'cal/calendar.html', context)

# url에서 전달된 년도와 월 정보를 추출하여, datetime 객체로 변환하는 함수
def get_date(req_day):
    try:
        if req_day:
            year, month, day = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
    except (ValueError, TypeError):
        pass
    return datetime.today().date()

# 주어진 날짜의 이전 달을 계산
def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    a = 'day=' + str(prev_month.year) + '-' + str(prev_month.month) + '-' + str(prev_month.day)
    return a

# 주어진 날짜의 다음 달을 계산
def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    a = 'day=' + str(next_month.year) + '-' + str(next_month.month) + '-' + str(next_month.day)
    return a