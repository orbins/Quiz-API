from django.contrib import admin
from .models import Categories, Quizzes, Questions, Answers
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(Categories)
class CatAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Quizzes)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category']


# Не регистрирую
class AnswerInlineModel(admin.TabularInline):
    model = Answers
    # Модель к которой относится
    fields = ['text', 'is_right']


@admin.register(Questions)
class QuestionAdmin(admin.ModelAdmin):
    save_on_top = True
    fields = ['title', 'quiz', 'kind', 'difficulty', 'is_active']
    list_display = ['id', 'title', 'quiz', 'kind',
                    'difficulty', 'date_updated']
    inlines = [AnswerInlineModel, ]


@admin.register(Answers)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'is_right', 'question']

