from operator import attrgetter

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.views.generic import (
    View,
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from accounts.models import UserProfile
from quiz.models import Quiz, Question, Score
from quiz.forms import quiz_forms, QuizForm, QuestionFormset


def get_quiz_queryset(*filters, query=None, order_by=None):
    queryset = []
    queries = query.split(" ")
    for q in queries:
        quizzes = Quiz.objects.filter(
            Q(title__icontains=q) |
            Q(summary__icontains=q)
        ).distinct()
        if filters:
            for filter_dict in filters:
                variable_column = filter_dict.get('column')
                search_type = filter_dict.get('search_type')
                search_value = filter_dict.get('search_value')
                filter_param = variable_column + '__' + search_type if search_type else variable_column
                quizzes = quizzes.filter(**{filter_param: search_value})

        for quiz in quizzes:
            queryset.append(quiz)

    if order_by:
        return sorted(list(set(queryset)), key=attrgetter(order_by), reverse=True)
    return list(set(queryset))


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


class QuizListView(ListView):
    model = Quiz
    template_name = "quiz/quiz_list.html"
    context_object_name = 'quiz_list'

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query:
            quizzes = get_quiz_queryset(
                {'column': 'status', 'search_value': 2},
                {'column': 'published_date', 'search_type': 'lte', 'search_value': timezone.now()},
                query=query,
                order_by='published_date'
            )
        else:
            quizzes = Quiz.objects.filter(published_date__lte=timezone.now()).filter(status=2).order_by('-published_date')

        return quizzes

    def get_context_data(self, **kwargs):
        context = super(QuizListView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['query'] = str(query)
        return context


class QuizDraftsListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quiz/quiz_drafts_list.html"
    context_object_name = 'quiz_list'

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query:
            quizzes = get_quiz_queryset(
                {'column': 'status', 'search_value': 1},  # drafts
                {'column': 'author', 'search_type': 'user', 'search_value': self.request.user},  # personal drafts
                query=query,
                order_by='created'
            )
        else:
            quizzes = Quiz.objects.filter(author__user=self.request.user).filter(status=1).order_by('-created')
        return quizzes

    def get_context_data(self, **kwargs):
        context = super(QuizDraftsListView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['query'] = str(query)
        return context


class PersonalQuizzesView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quiz/personal_quizzes.html"
    context_object_name = 'quiz_list'

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query:
            quizzes = get_quiz_queryset(
                {'column': 'status', 'search_type': 'gt', 'search_value': 1},  # exclude drafts
                {'column': 'author', 'search_type': 'user', 'search_value': self.request.user},
                query=query,
                order_by='created'
            )
        else:
            quizzes = Quiz.objects.filter(author__user=self.request.user).exclude(status=1).order_by('-created')
        return quizzes

    def get_context_data(self, **kwargs):
        context = super(PersonalQuizzesView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['query'] = str(query)
        return context


class QuizDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, slug__iexact=kwargs.get("slug"))
        has_rights_to_edit = self.request.user.is_authenticated and (
                    quiz.author.user == self.request.user or self.request.user.is_superuser)
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
            }
            return render(request, 'quiz/quiz_score.html', context)
        except Score.DoesNotExist:
            form_list = quiz_forms(quiz)
            context = {
                'form_list': form_list,
                'quiz': quiz,
                'has_rights_to_edit': has_rights_to_edit,
            }
            return render(request, 'quiz/quiz_detail.html', context)


class QuizPublishView(LoginRequiredMixin, View):
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


class QuestionDetailView(DetailView):
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


class CreateQuizView(LoginRequiredMixin,CreateView):

    model = Quiz
    form_class = QuizForm

    def form_valid(self, form, **kwargs):
        quiz = form.save(commit=False)
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        quiz.author = user_profile
        quiz.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = QuizForm(request.POST)
        if form.is_valid():
            self.form_valid(form, **kwargs)

        return redirect(reverse('questions-edit', kwargs={'pk': self.object.pk}))


class QuizUpdateView(UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name_suffix = '_update_form'
    context_object_name = 'quiz'

    def get_success_url(self):
        return reverse('questions-edit', kwargs={'pk': self.object.pk})


class QuizDeleteView(DeleteView):
    model = Quiz

    def get_success_url(self):
        return reverse('personal-quizzes')


def edit_questions(request, pk):
    """Edit questions and their answers for a single quiz."""

    quiz = get_object_or_404(Quiz, id=pk)

    if request.method == 'POST':
        formset = QuestionFormset(request.POST, instance=quiz, prefix='questions')
        if formset.is_valid():
            formset.save()
            if quiz.status == 2:  # public
                quiz.publish()
            return redirect('quiz-detail', slug=quiz.slug)
    else:
        formset = QuestionFormset(instance=quiz, prefix='questions')

    return render(request, 'quiz/edit_questions.html', {
        'quiz': quiz,
        'question_formset': formset})
