import re

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


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
    author = models.ForeignKey('Author', related_name='author', on_delete=models.SET_NULL, null=True)
    slug = models.SlugField('slug')
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the test")
    category = models.ManyToManyField(Category, help_text="Select a topic for this quiz")
    publish = models.DateTimeField('publish')
    students = models.ManyToManyField(User, blank=True, related_name='students')
    created = models.DateTimeField('created', auto_now_add=True)

    class Meta:
        verbose_name = 'quiz'
        verbose_name_plural = 'quizzes'
        db_table = 'quizzes'
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('quiz-detail', args=[str(self.id)])

    # def get_absolute_url(self):
    #     return reverse('quiz_detail', kwargs={
    #         'slug': self.slug,
    #     })

    def display_category(self):
        return ', '.join([category.name for category in self.category.all()[:3]])

    def count_questions(self):
        return Question.objects.filter(quiz=self).count()

    def get_process_quiz_url(self):
        return reverse('process_quiz', kwargs={
            'slug': self.slug,
        })

    display_category.short_description = 'Topic'


class Question(models.Model):
    question = models.TextField(max_length=200, default="")
    option1 = models.CharField(max_length=50, default="")
    option2 = models.CharField(max_length=50, default="")
    option3 = models.CharField(max_length=50, default="")
    option4 = models.CharField(max_length=50, default="")
    answer = models.CharField(max_length=50, default="")
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.question

    def display_quiz(self):
        """
        Creates a string for the quiz. This is required to display quiz in Admin.
        """
        return self.quiz.title


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()

    def get_absolute_url(self):
        return reverse('author-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{0}, {1}'.format(self.last_name, self.first_name)


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
        return reverse('quiz_detail', kwargs={
            'slug': self.quiz.slug,
        })

    @property
    def correct_answer_count(self):
        return self.correct_answers.count()

    @property
    def total_questions(self):
        return self.quiz.count_questions

    def __str__(self):
        return u"%s took the quiz %s" % (self.student, self.quiz)
