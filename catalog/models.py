from django.db import models
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User


# Create your models here.
class Topic(models.Model):
    """
    Model representing a quiz topic (e.g. Math, Programming, English etc.)
    """
    name = models.CharField(max_length=200, help_text="Enter a quiz topic (e.g. Math, Programming, English etc.)")
    
    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name


class Quiz(models.Model):
    """
    Model representing a test (but not a test itself).
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because quiz can only have one author, but authors can have multiple quizes
    # Author as a string rather than object because it hasn't been declared yet in the file.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the test")
    topic = models.ManyToManyField(Topic, help_text="Select a topic for this quiz")
    # ManyToManyField used because genre can contain many books. Quizs can cover many topics.
    # Topic class has already been defined so we can specify the object above.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    passed_date = models.DateField(null=True, blank=True)
    PASS_STATUS = (
        ('p', 'passed'),
        ('n', 'not passed'),
    )

    status = models.CharField(max_length=1, choices=PASS_STATUS, blank=True, default='n',
                              help_text='Is the quiz passed')

    class Meta:
        ordering = ["passed_date"]
    
    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns the url to access a particular quiz instance.
        """
        return reverse('quiz-detail', args=[str(self.id)])

    def display_topic(self):
        """
        Creates a string for the Topic. This is required to display topic in Admin.
        """
        return ', '.join([topic.name for topic in self.topic.all()[:3]])

    display_topic.short_description = 'Topic'


class Question(models.Model):
    question = models.TextField(max_length=200, default="")
    option1 = models.CharField(max_length=50, default="")
    option2 = models.CharField(max_length=50, default="")
    option3 = models.CharField(max_length=50, default="")
    option4 = models.CharField(max_length=50, default="")
    answer = models.CharField(max_length=50, default="")
    exam = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.question

    def display_quiz(self):
        """
        Creates a string for the quiz. This is required to display quiz in Admin.
        """
        return self.exam.name


class Author(models.Model):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # date_of_birth = models.DateField(null=True, blank=True)

    def get_absolute_url(self):
        """
        Returns the url to access a particular author instance.
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the Model object.
        """
        return '{0}, {1}'.format(self.last_name, self.first_name)