from django.shortcuts import render
from .models import Quiz, Author, Topic, Question
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

    num_math_quizzes = Quiz.objects.filter(title__contains='math').count()

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'num_quizzes': num_quizzes,
                 'num_passed': num_passed,
                 'num_authors': num_authors,
                 'num_math_quizzes': num_math_quizzes,
                 },
    )


from django.views import generic


class QuizListView(generic.ListView):
    model = Quiz

    # to filter by some word
    # def get_queryset(self):
    #     return Quiz.objects.filter(title__icontains='translat')[:5]

    def get_context_data(self, **kwargs):
        # В первую очередь получаем базовую реализацию контекста
        context = super(QuizListView, self).get_context_data(**kwargs)
        # Добавляем новую переменную к контексту и иниуиализируем ее некоторым значением
        context['some_data'] = 'This is just some data'
        return context


class QuizDetailView(generic.DetailView):
    model = Quiz


class QuestionDetailView(generic.DetailView):
    model = Question

