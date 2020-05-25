import re

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.template.defaultfilters import truncatewords_html
from django.utils import timezone
from accounts.models import UserProfile


class CategoryManager(models.Manager):

    def new_category(self, category):
        new_category = self.create(category=re.sub('\s+', '-', category).lower())

        new_category.save()
        return new_category


class Category(models.Model):
    name = models.CharField(
        verbose_name="category",
        max_length=250, blank=True,
        unique=True, null=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Quiz(models.Model):
    STATUS_CHOICES = (
        (1, 'draft'),
        (2, 'public'),
        (3, 'close'),
    )
    title = models.CharField(max_length=200)
    author = models.ForeignKey(UserProfile, related_name='author', on_delete=models.SET_NULL, null=True)
    slug = models.SlugField('slug')
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the test")
    category = models.ManyToManyField(Category, help_text="Select a topic for this quiz")
    status = models.IntegerField('status', choices=STATUS_CHOICES, default=1)
    published_date = models.DateTimeField('published_date', null=True, blank=True)
    students = models.ManyToManyField(User, blank=True, related_name='students')
    created = models.DateTimeField('created', auto_now_add=True)

    class Meta:
        verbose_name = 'quiz'
        verbose_name_plural = 'quizzes'
        db_table = 'quizzes'
        ordering = ('-published_date',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('quiz-detail', kwargs={
            'slug': self.slug,
        })

    def display_category(self):
        return ', '.join([category.name for category in self.category.all()[:3]])

    def count_questions(self):
        return Question.objects.filter(quiz=self).count()

    def get_process_quiz_url(self):
        return reverse('process-quiz', kwargs={
            'slug': self.slug,
        })

    def publish(self):
        self.published_date = timezone.now()
        self.status = 2
        self.save()

    def close(self):
        self.status = 3
        self.save()

    def get_status(self):
        statuses = dict(self.STATUS_CHOICES)
        return statuses[self.status]

    display_category.short_description = 'Category'


class Question(models.Model):
    question = models.CharField(max_length=200, default="")
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'question'
        verbose_name_plural = 'questions'
        db_table = 'quiz_questions'

    def display_quiz(self):
        """
        Creates a string for the quiz. This is required to display quiz in Admin.
        """
        return self.quiz.title

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in Answer.objects.filter(question=self)]

    @property
    def correct_answer(self):
        return Answer.objects.filter(question=self).filter(correct=True)[0] if Answer.objects.filter(question=self).filter(correct=True).count() else None

    @property
    def title(self):
        return u"%s" % truncatewords_html(self.question, 10)

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    content = models.CharField('answer', max_length=200)
    weight = models.IntegerField('weight', default=1)
    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Is this a correct answer?",
                                  verbose_name="Correct")

    class Meta:
        verbose_name = 'answer'
        verbose_name_plural = 'answers'
        db_table = 'quiz_answers'
        ordering = ("weight",)

    def __str__(self):
        return u"%s" % truncatewords_html(self.content, 10)


class Score(models.Model):
    student = models.ForeignKey(User, related_name='student', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    correct_answers = models.ManyToManyField(Question, blank=True)
    quiz_taken = models.DateTimeField('quiz taken', auto_now_add=True)

    class Meta:
        verbose_name = 'student score'
        verbose_name_plural = 'student scores'
        db_table = 'quiz_scores'
        unique_together = (("student", "quiz"),)

    class Admin:
        list_display = ('quiz', 'student', 'correct_answer_count', 'total_questions',)
        list_filter = ('quiz', 'student')

    def get_absolute_url(self):
        return reverse('quiz-detail', kwargs={
            'slug': self.quiz.slug,
        })

    @property
    def get_correct_answers(self):
        return [q.question for q in self.correct_answers.all()]

    @property
    def correct_answer_count(self):
        return self.correct_answers.count()

    @property
    def total_questions(self):
        return self.quiz.count_questions

    def __str__(self):
        return u"%s took the quiz %s" % (self.student, self.quiz)
