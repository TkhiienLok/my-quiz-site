from django.shortcuts import render
from django.views import generic
from django.core.exceptions import PermissionDenied

from .models import Quiz, Author, Question


def index(request):
    """ home page """
    num_quizzes = Quiz.objects.all().count()
    num_authors = Author.objects.count()
    num_math_quizzes = Quiz.objects.filter(title__contains='math').count()
    return render(
        request,
        'index.html',
        context={'num_quizzes': num_quizzes,
                 'num_authors': num_authors,
                 'num_math_quizzes': num_math_quizzes,
                 },
    )


class QuizListView(generic.ListView):
    model = Quiz

    def get_context_data(self, **kwargs):
        context = super(QuizListView, self).get_context_data(**kwargs)
        context['some_data'] = 'This is just some data'
        return context


class QuizDetailView(generic.DetailView):
    model = Quiz

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied


class QuestionDetailView(generic.DetailView):
    model = Question

