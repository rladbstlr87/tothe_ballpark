from django.urls import path
from . import views

app_name = 'cal'

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar')
]