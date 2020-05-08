from django.contrib import admin
from .models import Author, Category, Quiz,  Question, Score

admin.site.register(Category)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    fields = ['first_name', 'last_name']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish', 'display_category')
    list_filter = ('title', 'category')
    inlines = [QuestionInline]


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'correct_answer_count', 'total_questions',)
    list_filter = ('quiz', 'student')


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Author, AuthorAdmin)
