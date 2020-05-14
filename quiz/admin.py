from django.contrib import admin
import nested_admin
from quiz.models import Category, Quiz,  Question, Score, Answer

admin.site.register(Category)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'correct_answer_count', 'total_questions',)
    list_filter = ('quiz', 'student')


class AnswerInline(nested_admin.NestedStackedInline):
    model = Answer


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [AnswerInline]


class QuizAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestionInline]


admin.site.register(Quiz, QuizAdmin)
