from django.contrib import admin
from .models import Author, Topic, Quiz, QuizInstance, Question

# Register your models here.
# admin.site.register(Quiz)
# admin.site.register(Author)
admin.site.register(Topic)
# admin.site.register(QuizInstance)
# admin.site.register(Question)

class QuizsInline(admin.TabularInline):
    model = Quiz

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    fields = ['first_name', 'last_name']
    inlines = [QuizsInline]


# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)


class QuizsInstanceInline(admin.TabularInline):
    model = QuizInstance
# Register the Admin classes for Quiz using the decorator


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_topic')
    inlines = [QuizsInstanceInline]


# Register the Admin classes for QuizInstance using the decorator

@admin.register(QuizInstance)
class QuizInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', )
    fieldsets = (
        (None, {
            'fields': ('quiz', 'id')
        }),
        ('Passed status', {
            'fields': ('status',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'exam')
