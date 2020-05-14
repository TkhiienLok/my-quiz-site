from operator import attrgetter

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q

from quiz.models import Quiz, Question, Score
from quiz.forms import quiz_forms


def index(request):
    """ home page """
    num_quizzes = Quiz.objects.all().count()
    num_math_quizzes = Quiz.objects.filter(title__contains='math').count()
    context = {
        'num_quizzes': num_quizzes,
        'num_math_quizzes': num_math_quizzes,
    }
    student = request.user
    if request.user.is_authenticated:
        quizzes = Quiz.objects.filter(students=student)
        scores = Score.objects.filter(student=student)
        context['quizzes'] = quizzes
        context['scores'] = scores
    return render(request, 'index.html', context)


class QuizListView(generic.ListView):
    model = Quiz
    template_name = "quiz/quiz_list.html"
    context_object_name = 'quiz_list'

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query:
            quizzes = sorted(get_quiz_queryset(query), key=attrgetter('published_date'), reverse=True)
        else:
            quizzes = Quiz.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

        return quizzes

    def get_context_data(self, **kwargs):
        context = super(QuizListView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['query'] = str(query)
        return context


class QuizDetailView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, slug__iexact=kwargs.get("slug"))
        has_rights_to_edit = self.request.user.is_authenticated and (
                    quiz.author.user == self.request.user or self.request.user.is_superuser)
        quiz_status = quiz.get_status()
        try:
            score = quiz.score_set.get(student=self.request.user, quiz=quiz)
            questions = quiz.question_set.all()
            correct_answers = ",".join(score.get_correct_answers)
            context = {
                'quiz': quiz,
                'score': score,
                'questions': questions,
                'correct_answers_string': correct_answers,
                'has_rights_to_edit': has_rights_to_edit,
                'quiz_status': quiz_status
            }
            return render(request, 'quiz/quiz_score.html', context)
        except Score.DoesNotExist:
            form_list = quiz_forms(quiz)
            context = {'form_list': form_list, 'quiz': quiz, 'has_rights_to_edit': has_rights_to_edit, 'quiz_status': quiz_status}
            return render(request, 'quiz/quiz_detail.html', context)


class QuizPublishView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs.get("pk"))
        quiz.publish()
        return HttpResponseRedirect(quiz.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        user = request.user
        quiz = get_object_or_404(Quiz, pk=kwargs.get("pk"))
        if not (quiz.author.user == user or user.is_superuser):
            raise PermissionDenied
        return handler


class QuizCloseView(QuizPublishView):
    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=kwargs.get("pk"))
        quiz.close()
        return HttpResponseRedirect(quiz.get_absolute_url())


class QuestionDetailView(generic.DetailView):
    model = Question


def process_quiz(request, slug):
    quiz = get_object_or_404(Quiz, slug__iexact=slug)

    if request.method == 'POST':
        form_list = quiz_forms(quiz, request.POST)
        score = Score()
        score.student = request.user
        score.quiz = quiz
        score.save()

        for form in form_list:
            if form.is_correct():
                question = Question.objects.filter(question=form.question)[0]
                score.correct_answers.add(question)
                score.save()
        return HttpResponseRedirect(score.get_absolute_url())

    return HttpResponseRedirect(quiz.get_absolute_url())


def get_quiz_queryset(query=None):
    queryset = []
    queries = query.split(" ")
    for q in queries:
        quizzes = Quiz.objects.filter(published_date__lte=timezone.now()).filter(
            Q(title__icontains=q) |
            Q(summary__icontains=q)
        ).distinct()

        for quiz in quizzes:
            queryset.append(quiz)
    return list(set(queryset))
