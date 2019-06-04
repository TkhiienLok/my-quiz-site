from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
    path('', views.index, name='index'),
    url(r'^quizzes/$', views.QuizListView.as_view(), name='quizzes'),
    url(r'^quiz/(?P<pk>\d+)$', views.QuizDetailView.as_view(), name='quiz-detail'),  # или r'^quiz/(?P<stub>[-\w]+)$'   - для информативной ссылки
]
