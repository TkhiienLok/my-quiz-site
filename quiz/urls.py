from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('quizzes/', views.QuizListView.as_view(), name='quizzes'),
    path('draft-quizzes/', views.QuizDraftsListView.as_view(), name='quiz-drafts'),
    path('personal-quizzes/', views.PersonalQuizzesView.as_view(), name='personal-quizzes'),
    path('quiz/<slug>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('<pk>/update/', views.QuizUpdateView.as_view(), name='quiz-update'),
    path('<pk>/delete/', views.QuizDeleteView.as_view(), name='quiz-delete'),
    path('category/new/', views.CategoryCreateView.as_view(), name='category-new'),
    path('category/<pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('category/<pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('process-quiz/<slug>/', views.process_quiz, name='process-quiz'),
    path('quiz/<pk>/publish/', views.QuizPublishView.as_view(), name='quiz_publish'),
    path('quiz/<pk>/close/', views.QuizCloseView.as_view(), name='quiz_close'),
    path('quizzes/new/', views.CreateQuizView.as_view(), name='quiz-new'),
    path('quizzes/<pk>/edit/', views.edit_questions, name='questions-edit'),
]
