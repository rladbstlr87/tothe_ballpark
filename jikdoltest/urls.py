from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'jikdoltest'

urlpatterns = [
    path('start/', TemplateView.as_view(template_name='start.html'), name='start'),
    path('question/<int:step>', views.test_question, name='test_question'),
    path('result/', views.test_result, name='test_result'),  
    path('result/<str:type_code>/', views.result_share, name='result_share'),  
]