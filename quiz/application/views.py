from rest_framework import generics
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.contrib.auth import get_user_model

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
    Для просмотра списка всех
    существующих категорий и
    создания новых
    """
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Для обновления, добавления
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
    # для оптимизации использую only и select_related
    queryset = Quizzes.objects.select_related(
        'category').only('id', 'title', 'category__name', 'author').all()
    serializer_class = QuizSerializer


class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление
    и удаление квиза
    """
    queryset = Quizzes.objects.select_related(
        'category').only('title', 'category__name', 'date_created').all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthorOrReadOnly]


class QuizQuestions(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    lookup_url_kwarg = 'topic'

    def get_queryset(self):
        return Questions.objects.prefetch_related('answers').select_related(
                                                            'quiz').filter(quiz__title=self.kwargs['topic']).filter(is_active=True)


class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    queryset = Questions.objects.prefetch_related('answers').select_related(
                                                            'quiz').all()
    permission_classes = [IsAuthorOrReadOnly]


class RandomQuestion(generics.ListAPIView):
    serializer_class = QuestionSerializer
    lookup_url_kwarg = 'topic'

    def get_queryset(self):
        return Questions.objects.prefetch_related('answers').select_related(
                'quiz').filter(quiz__title=self.kwargs['topic']).filter(is_active=True).order_by('?')[:1]


class AnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SingleAnswerSerializer
    queryset = Answers.objects.select_related('question').only('id', 'text', 'is_right', 'question__title').all()
    permission_classes = [IsAuthorOrReadOnly]


class AddAnswer(generics.CreateAPIView):
    serializer_class = SingleAnswerSerializer


class RegisterView(generics.CreateAPIView):
    """
    Контроллер для регистрации пользователей
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
