from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('quizzes/', views.QuizListView.as_view(), name='quizzes'),
    path('quiz/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),  # or 'quiz/<stub>/' for informative link
]
