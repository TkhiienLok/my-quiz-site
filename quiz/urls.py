from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('quizzes/', views.QuizListView.as_view(), name='quizzes'),
    path('quiz/<slug>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('process-quiz/<slug>/', views.process_quiz, name='process-quiz'),
    path('quiz/<pk>/publish/', views.QuizPublishView.as_view(), name='quiz_publish'),
    path('quiz/<pk>/close/', views.QuizCloseView.as_view(), name='quiz_close'),
]
