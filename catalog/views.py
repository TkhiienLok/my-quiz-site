from django.shortcuts import render
from .models import Quiz, Author, QuizInstance, Topic
# Create your views here.


def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    # Генерация "количеств" некоторых главных объектов
    num_quizzes = Quiz.objects.all().count()
    # Пройденные тесты (статус = 'p')
    num_passed = Quiz.objects.filter(status__exact='p').count()
    num_authors = Author.objects.count()  # Метод 'all()' применен по умолчанию.

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'num_quizzes': num_quizzes,
                 'num_instances_passed': num_passed, 'num_authors': num_authors},
    )
