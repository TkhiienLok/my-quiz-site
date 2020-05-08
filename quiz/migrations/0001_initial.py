# Generated by Django 3.0.6 on 2020-05-08 11:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True, unique=True, verbose_name='category')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(verbose_name='slug')),
                ('summary', models.TextField(help_text='Enter a brief description of the test', max_length=1000)),
                ('publish', models.DateTimeField(verbose_name='publish')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author', to='quiz.Author')),
                ('category', models.ManyToManyField(help_text='Select a topic for this quiz', to='quiz.Category')),
                ('students', models.ManyToManyField(blank=True, related_name='students', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'quiz',
                'verbose_name_plural': 'quizzes',
                'db_table': 'quizzes',
                'ordering': ('-publish',),
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(default='', max_length=200)),
                ('option1', models.CharField(default='', max_length=50)),
                ('option2', models.CharField(default='', max_length=50)),
                ('option3', models.CharField(default='', max_length=50)),
                ('option4', models.CharField(default='', max_length=50)),
                ('answer', models.CharField(default='', max_length=50)),
                ('quiz', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz.Quiz')),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quiz_taken', models.DateTimeField(auto_now_add=True, verbose_name='quiz taken')),
                ('correct_answers', models.ManyToManyField(blank=True, to='quiz.Question')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Quiz')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'student score',
                'verbose_name_plural': 'student scores',
                'db_table': 'quiz_scores',
                'unique_together': {('student', 'quiz')},
            },
        ),
    ]
