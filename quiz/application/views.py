from rest_framework import generics
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.contrib.auth import get_user_model
from django.http import Http404


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
        'categories': reverse('categories', request=request, format=format),
        'quizzes': reverse('quizzes', request=request, format=format),
    })


class CategoryList(generics.ListCreateAPIView):
    """
    Для просмотра списка всех существующих категорий и
    создания новых с возможностью фильтрации по автору
    """
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ('author', )


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Для обновления, получения
    и удаления категорий доступно
    только их авторам
    """
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthorOrReadOnly]


class QuizList(generics.ListCreateAPIView):
    """
    Получение списка квизов
    """
    serializer_class = QuizSerializer
    filterset_fields = ('author', 'category')

    def get_queryset(self):
        # С целью оптимизации нельзя получить все квизы
        # Только с фильтрацией по автору или категории
        if len(self.request.query_params) == 0:
            return Quizzes.objects.none()
        return Quizzes.objects.select_related('category').all()


class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление
    и удаление квиза
    """
    queryset = Quizzes.objects.select_related('category').all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthorOrReadOnly]


class QuizQuestions(generics.ListCreateAPIView):
    """
    Получение списка вопросов и создание вопроса
    """
    serializer_class = QuestionSerializer
    filterset_fields = ('quiz', 'author')

    def get_queryset(self):
        # Только с фильтрацией по автору или квизу
        if len(self.request.query_params) == 0:
            return Questions.objects.none()
        return Questions.objects.prefetch_related(
                    'answers').select_related(
                    'quiz').filter(is_active=True)


class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Обновление, удаление, чтение конкретного вопроса,
    доступно только для автора самого вопроса
    """
    serializer_class = QuestionSerializer
    queryset = Questions.objects.prefetch_related('answers').select_related('quiz').all()
    permission_classes = [IsAuthorOrReadOnly]


class RandomQuestion(generics.ListAPIView):
    """Получение случайного вопроса"""
    serializer_class = QuestionSerializer
    lookup_field = 'quiz'

    def get_queryset(self):
        quiz = self.kwargs.get('quiz')
        # только по квизу
        return Questions.objects.prefetch_related('answers').select_related(
                'quiz').filter(is_active=True, quiz=quiz).order_by('?')[:1]


class AnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Чтение, обновление и удаление ответа на вопрос,
    доступно только для автора
    """
    serializer_class = SingleAnswerSerializer
    queryset = Answers.objects.select_related('question').all()
    permission_classes = [IsAuthorOrReadOnly]


class AnswerList(generics.ListCreateAPIView):
    """
    Создание ответа на вопрос,
    текущий пользователь автоматически определяется
    в качестве автора
    """
    serializer_class = SingleAnswerSerializer
    filterset_fields = ('question', )

    def get_queryset(self):
        if len(self.request.query_params) == 0:
            return Answers.objects.none()
        return Answers.objects.select_related('question').all()


class RegisterView(generics.CreateAPIView):
    """
    Контроллер для регистрации пользователей
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
