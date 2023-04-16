from rest_framework import generics
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django_filters import rest_framework as filters

from django.contrib.auth import get_user_model

from .filters import CategoryFilter
from .permissions import IsAuthorOrReadOnly
from .models import Quizzes, Categories, Questions, Answers
from .serializers import (QuizSerializer, QuestionSerializer,
                          CategorySerializer, SingleAnswerSerializer,
                          UserSerializer)

User = get_user_model()


@api_view(['GET'])
# Переадресация на вход\регистрацию реализовывается на фронте
def api_root(request, format=None):
    """
    Контроллер для корневого url,
    возвращает url'ы для просмотра
    списков квизов и их категорий
    """
    return Response({
        'categories': reverse('categories',
                              request=request,
                              format=format),
        'quizzes': reverse('quizzes',
                           request=request,
                           format=format),
        'questions': reverse('questions',
                             request=request,
                             format=format)
    })


class CategoryList(generics.ListCreateAPIView):
    """
    Для просмотра списка всех существующих категорий и
    создания новых с возможностью фильтрации по автору
    """
    queryset = Categories.objects.select_related(
        'author').only('id',
                       'name',
                       'author__username').all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Для обновления, получения
    и удаления категорий доступно
    только их авторам
    """
    queryset = Categories.objects.select_related(
        'author').only('id',
                       'name',
                       'author__username').all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthorOrReadOnly]


class QuizList(generics.ListCreateAPIView):
    """
    Получение списка квизов
    """
    serializer_class = QuizSerializer
    filterset_fields = ('author', 'category')

    def get_queryset(self):
        return Quizzes.objects.select_related(
            'category', 'author').only('id',
                                       'title',
                                       'category__name',
                                       'author__username').all()


class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление
    и удаление квиза
    """
    queryset = Quizzes.objects.select_related(
        'category', 'author').only('id',
                                    'title',
                                    'category__name',
                                    'author__username').all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthorOrReadOnly]


class QuizQuestions(generics.ListCreateAPIView):
    """
    Получение списка вопросов и создание вопроса
    """
    serializer_class = QuestionSerializer
    filterset_fields = ('quiz', 'author', 'is_active')

    def get_queryset(self):
        return Questions.objects.prefetch_related(
                'answers').select_related(
                'quiz', 'author').all()


class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Обновление, удаление, чтение конкретного вопроса,
    доступно только для автора самого вопроса
    """
    serializer_class = QuestionSerializer
    queryset = Questions.objects.prefetch_related(
        'answers').select_related('quiz').all()
    permission_classes = [IsAuthorOrReadOnly]


class RandomQuestion(generics.ListAPIView):
    """Получение случайного вопроса"""
    serializer_class = QuestionSerializer
    lookup_field = 'quiz_id'

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        # только по квизу
        return Questions.objects.prefetch_related('answers').select_related(
                'quiz').filter(is_active=True, quiz=quiz_id).order_by('?')[:1]


class AnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Чтение, обновление и удаление ответа на вопрос,
    доступно только для автора
    """
    serializer_class = SingleAnswerSerializer
    queryset = Answers.objects.select_related(
        'question').only('question__title', 'id',
                         'text', 'is_right',
                         'author__username').all()
    permission_classes = [IsAuthorOrReadOnly]


class AddAnswer(generics.CreateAPIView):
    """
    Создание ответа на вопрос,
    текущий пользователь автоматически определяется
    в качестве автора
    """
    serializer_class = SingleAnswerSerializer


class RegisterView(generics.CreateAPIView):
    """
    Контроллер для регистрации пользователей
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
