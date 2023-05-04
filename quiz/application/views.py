from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .filters import CategoryFilter, QuizFilter
from .models import (
    Answers,
    Categories,
    Quizzes,
    Questions,
)
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CategorySerializer,
    QuizSerializer,
    QuestionSerializer,
    SingleAnswerSerializer,
    UserSerializer,
)

User = get_user_model()


@api_view(['GET'])
# Переадресация на вход\регистрацию реализовывается на фронте
def api_root(request, format=None):
    """
    Для просмотра
    списков категорий, квизов и вопросов
    """
    return Response({
        'categories': reverse('application:categories',
                              request=request,
                              format=format),
        'quizzes': reverse('application:quizzes',
                           request=request,
                           format=format),
        'questions': reverse('application:questions',
                             request=request,
                             format=format)
    })


class CategoryList(generics.ListCreateAPIView):
    """
    Просмотр списка всех существующих категорий и
    создание новых с возможностью фильтрации по имени
    """
    queryset = Categories.objects.only('id', 'name').all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
    http_method_names = ['post', 'get']


class QuizList(generics.ListCreateAPIView):
    """
    Просмотр списка всех квизов с возможностью фильтрации
    по именам авторов и категорий. Создание квиза от автора.
    """
    serializer_class = QuizSerializer
    filterset_class = QuizFilter
    http_method_names = ('post', 'get')

    def get_queryset(self):
        return Quizzes.objects.select_related(
            'category', 'author').only('id',
                                       'title',
                                       'category__name',
                                       'author__username',).all()


class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление и удаление квиза,
    обновление и удаление доступно только для автора квиза
    """
    queryset = Quizzes.objects.select_related(
        'category', 'author').only('id',
                                   'title',
                                   'category__name',
                                   'author__username').all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthorOrReadOnly]
    http_method_names = ['patch', 'get', 'delete']


class QuizQuestions(generics.ListCreateAPIView):
    """
    Получение списка вопросов и создание вопроса
    """
    serializer_class = QuestionSerializer
    filterset_fields = ('quiz', 'author', 'is_active')
    http_method_names = ['post', 'get']

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
    http_method_names = ['patch', 'get', 'delete']


class RandomQuestion(generics.ListAPIView):
    """Получение случайного вопроса"""
    serializer_class = QuestionSerializer
    lookup_field = 'quiz_id'
    http_method_names = ['get']

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
    http_method_names = ['patch', 'get', 'delete']


class AddAnswer(generics.CreateAPIView):
    """
    Создание ответа на вопрос,
    текущий пользователь автоматически определяется
    в качестве автора
    """
    serializer_class = SingleAnswerSerializer
    http_method_names = ['post']


class RegisterView(generics.CreateAPIView):
    """
    Создание пользователя
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']
    