from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
# Добавляет переводимость строкам

User = get_user_model()


class Categories(models.Model):
    """Модель категорий квизов"""
    name = models.CharField(max_length=255,
                            verbose_name="Имя")

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

    def __str__(self):
        return self.name


class Quizzes(models.Model):
    """Модель квизов"""
    title = models.CharField(max_length=255, default=_("New Quiz"),
                             verbose_name=_("Имя"))
    category = models.ForeignKey(Categories, default=1,
                                 on_delete=models.CASCADE,
                                 verbose_name="Категория")
    # 1 квиз относится к 1 категории
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name="Дата создания")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name="Автор")

    class Meta:
        verbose_name = _("Квиз")
        verbose_name_plural = _("Квизы")
        ordering = ['id']

    def __str__(self):
        return self.title


class Updated(models.Model):
    # Абстрактный класс, полезен, когда нужно поместить
    # общие свойства в несколько моделей
    # для добавления свойства отслеживания обновлений
    date_updated = models.DateTimeField(
        verbose_name=_("Дата последнего изменения"), auto_now=True
    )

    class Meta:
        abstract = True


class Questions(Updated):
    """Модель для вопросов"""

    # сложность вопроса
    SCALE = (
        (0, _('Fundamental')),
        (1, _('Beginner')),
        (2, _('Intermediate')),
        (3, _('Advanced')),
        (4, _('Expert')),
    )

    # Тип вопроса, с одним ответом или несколькими
    STYLE = (
        (0, _('Multiple choice')),
        (1, _('Single Choice')),
    )

    # 1 вопрос может относиться к 1 квизу
    quiz = models.ForeignKey(Quizzes, related_name='questions',
                             on_delete=models.CASCADE,
                             verbose_name="Квиз")
    title = models.CharField(max_length=500,
                             verbose_name="Текс")
    kind = models.IntegerField(choices=STYLE, default=0,
                               verbose_name=_("Тип"))
    difficulty = models.IntegerField(choices=SCALE, default=0,
                                     verbose_name=_("Сложность"))
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_("Дата создания"))
    is_active = models.BooleanField(default=True,
                                    verbose_name=_("Статус"))
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name="Автор")

    class Meta:
        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")
        ordering = ['id']

    def __str__(self):
        return self.title


class Answers(Updated):
    """Модель для ответов на вопрос"""

    # 1 ответ относится только к 1 вопросу
    question = models.ForeignKey(Questions, related_name='answers',
                                 on_delete=models.CASCADE,
                                 verbose_name="Вопрос")
    text = models.TextField(max_length=500,
                            verbose_name=_("Текст"))
    is_right = models.BooleanField(default=False,
                                   verbose_name="Правильный?")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name="Автор")

    class Meta:
        verbose_name = _("Ответ")
        verbose_name_plural = _("Ответы")
        ordering = ['id']

    def __str__(self):
        return self.text

