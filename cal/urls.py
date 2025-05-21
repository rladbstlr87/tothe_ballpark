from django.urls import path
from . import views

app_name = 'cal'

urlpatterns = [
    path('', views.CalendarViews.as_view(), name='calendar')
    
]