from django.contrib import admin
from .models import Author, Category, Quiz,  Question, Score

admin.site.register(Category)


class QuizzesInline(admin.TabularInline):
    model = Quiz
    extra = 1


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    fields = ['first_name', 'last_name']
    inlines = [QuizzesInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_category')
    list_filter = ('title', 'category')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'quiz')
    list_filter = ('quiz',)
    search_fields = ('question',)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'correct_answer_count', 'total_questions',)
    list_filter = ('quiz', 'student')


admin.site.register(Author, AuthorAdmin)
