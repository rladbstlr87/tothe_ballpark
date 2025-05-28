from django.urls import path
from . import views

app_name = 'cal'

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<int:game_id>/', views.lineup, name='lineup'),
    path('<int:game_id>/attendance', views.attendance, name='attendance'),
]