from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta, date
from django.views import generic
from django.utils.safestring import mark_safe
import calendar
from .models import * 
from .utils import Calendar 
# Create your views here.

# django의 generic.listview 클래스를 상속받아서, 우리의 game 모델을 이용해 db에서 달력에 보여줄 이벤트들을 가져오는 뷰 
class CalendarViews(generic.ListView):
    model = Game
    template_name = 'cal/calendar.html'
    
    # context 데이터를 가져오는 함수로, 현재 달력에 보여줄 년도와 월 정보를 가져오고 calendar 클래스의 인스턴스를 생성성
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        
        # use today's date for the Calendar
        d = get_date(self.request.GET.get('day', None))
        
        cal = Calendar(d.year, d.month)
        
        # 달력을 html 형식으로 반환하고, 이를 템플릿에서 활용할 수 있도록 context에 저장함
        html_cal = cal.formatmonth(withyear= True)
        context['calendar'] = mark_safe(html_cal)
        
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        
        return context
    
# url에서 전달된 년도와 월 정보를 추출하여, datetime 객체로 변환하는 함수로, 위에서 선언한 get_context_data 함수 내에서 호출됨됨
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


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    a = 'day=' + str(next_month.year) + '-' + str(next_month.month) + '-' + str(next_month.day)
    return a
