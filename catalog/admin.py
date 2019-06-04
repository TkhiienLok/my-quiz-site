from django.contrib import admin
from .models import Author, Topic, Quiz,  Question

# Register your models here.
# admin.site.register(Quiz)
# admin.site.register(Author)
admin.site.register(Topic)
# admin.site.register(Question)


class QuizzesInline(admin.TabularInline):
    model = Quiz


# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    fields = ['first_name', 'last_name']
    inlines = [QuizzesInline]


# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_topic')
    list_filter = ('status', 'title')
    # inlines = [QuizzesInstanceInline]


# Register the Admin classes for Question using the decorator

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'exam')
