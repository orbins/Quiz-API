from django.contrib import admin
from .models import Categories, Quizzes, Questions, Answers
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(Categories)
class CatAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']
    ordering = ['id']


@admin.register(Quizzes)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'author']
    search_fields = ['title']
    search_help_text = 'Название квиза'
    list_filter = ('category', 'author',)
    list_display_links = ['id', 'title']
    ordering = ['id']
    empty_value_display = '-'


# Не регистрирую, вложенная модель в вопросы
class AnswerInlineModel(admin.TabularInline):
    model = Answers
    # Модель к которой относится
    fields = ['text', 'is_right']


@admin.register(Questions)
class QuestionAdmin(admin.ModelAdmin):
    save_on_top = True
    fields = ['title', 'quiz', 'kind', 'difficulty', 'is_active', 'author']
    list_display = ['id', 'title', 'quiz', 'kind',
                    'difficulty', 'date_updated', 'author']
    search_fields = ['title']
    search_help_text = 'Текст вопроса'
    list_filter = ('quiz', 'kind', 'difficulty', 'is_active', 'author')
    list_display_links = ['id', 'title']
    ordering = ['quiz']
    empty_value_display = '-'
    inlines = [AnswerInlineModel, ]
