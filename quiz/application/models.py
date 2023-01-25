from django.db import models
from django.utils.translation import gettext_lazy as _


class Categories(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class Quizzes(models.Model):
    title = models.CharField(max_length=255, default=_("New Quiz"),
                             verbose_name=_("Quiz title"))
    category = models.ForeignKey(Categories, default=1,
                                 on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")
        ordering = ['id']

    def __str__(self):
        return self.title


class Updated(models.Model):
    date_updated = models.DateTimeField(
        verbose_name=_("Last updated"), auto_now=True
    )

    class Meta:
        abstract = True


class Questions(Updated):
    SCALE = (
        (0, _('Fundamental')),
        (1, _('Beginner')),
        (2, _('Intermediate')),
        (3, _('Advanced')),
        (4, _('Expert')),
    )

    STYLE = (
        (0, _('Multiple choice')),
        (1, _('Single Choice')),
    )

    quiz = models.ForeignKey(Quizzes, related_name='questions',
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    kind = models.IntegerField(choices=STYLE, default=0,
                               verbose_name=_("Type of question"))
    difficulty = models.IntegerField(choices=SCALE, default=0,
                                     verbose_name=_("Difficulty"))
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_("Date Created"))
    is_active = models.BooleanField(default=False,
                                    verbose_name=_("Active Status"))

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['id']

    def __str__(self):
        return self.title


class Answers(Updated):
    question = models.ForeignKey(Questions, related_name='answers',
                                 on_delete=models.CASCADE)
    text = models.TextField(max_length=500,
                            verbose_name=_("Answer Text"))
    is_right = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
        ordering = ['id']

    def __str__(self):
        return self.text
