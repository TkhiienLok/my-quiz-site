from operator import attrgetter

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q, Count
from django.urls import reverse
from django.views.generic import (
    View,
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView
)

from accounts.models import UserProfile
from quiz.models import Quiz, Question, Score, Category
from quiz.forms import quiz_forms, QuizForm, QuestionFormset, CategoryForm


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
    authors_count = UserProfile.objects.annotate(num_quizzes=Count('author')).filter(num_quizzes__gt=0).count()

    context = {
        'num_quizzes': num_quizzes,
        'categories_count': Category.objects.count(),
        'authors_count': authors_count
    }

    student = request.user
    if request.user.is_authenticated:
        quizzes = Quiz.objects.filter(students=student)
        scores = Score.objects.filter(student=student).count()
        context['quizzes'] = quizzes
        context['num_passed'] = scores
    return render(request, 'index.html', context)


class QuizListView(ListView):
    model = Quiz
    template_name = "quiz/quiz_list.html"
    context_object_name = 'quiz_list'

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        category = self.request.GET.get('category', None)

        if query or category:
            filters = [{'column': 'status', 'search_value': 2},
                       {'column': 'published_date', 'search_type': 'lte', 'search_value': timezone.now()}]
            if category:
                category_objects = Category.objects.filter(name__contains=category)
                filters.append({'column': 'category', 'search_type': 'in', 'search_value': category_objects})
            quizzes = get_quiz_queryset(
                *filters,
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


def _get_form(request, formcls, prefix):
    data = request.POST if prefix in request.POST else None
    return formcls(data, prefix=prefix)


class CreateQuizView(TemplateView):
    template_name = 'quiz/quiz_form.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({'quiz_form': QuizForm(prefix='quiz-create'), 'category_form': CategoryForm(prefix='category-create')})

    def post(self, request, *args, **kwargs):
        quiz_form = _get_form(request, QuizForm, 'quiz-create')
        category_form = _get_form(request, CategoryForm, 'category-create')
        if quiz_form.is_bound and quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            user_profile = get_object_or_404(UserProfile, user=self.request.user)
            quiz.author = user_profile
            quiz.save()
            return redirect(reverse('questions-edit', kwargs={'pk': quiz.pk}))
        elif category_form.is_bound and category_form.is_valid():
            category_form.save()
        return self.render_to_response({'quiz_form': quiz_form, 'category_form': category_form})


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


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'quiz/category/category_create.html'
    context_object_name = 'category'

    def get_success_url(self):
        return reverse('category-list')


class CategoryListView(ListView):
    model = Category
    template_name = 'quiz/category/category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CategoryListView, self).get_context_data()
        math_categories = Category.objects.filter(name__contains='Math')
        context['math_categories'] = math_categories.count()
        context['num_math_quizzes'] = Quiz.objects.filter(category__in=math_categories).count()
        return context


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'quiz/category/category_update.html'
    context_object_name = 'category'

    def get_success_url(self):
        return reverse('category-list')


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'quiz/category/category_confirm_delete.html'
    context_object_name = 'category'

    def get_success_url(self):
        return reverse('category-list')
