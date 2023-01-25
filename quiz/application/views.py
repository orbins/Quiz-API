from rest_framework import generics
from .models import Quizzes, Categories, Questions, Answers
from .serializers import (QuizSerializer, QuestionSerializer,
                          CategorySerializer, SingleAnswerSerializer,
                          UserSerializer)
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .permissions import IsAuthorOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'categories': reverse('categories', request=request, format=format),
        'quizzes': reverse('quizzes', request=request, format=format),
    })


class CategoryList(generics.ListCreateAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthorOrReadOnly]


class QuizList(generics.ListCreateAPIView):
    queryset = Quizzes.objects.select_related(
        'category').only('id', 'title', 'category__name').all()
    serializer_class = QuizSerializer


class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quizzes.objects.select_related(
        'category').only('title', 'category__name', 'date_created').all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthorOrReadOnly]



class QuizQuestions(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    lookup_url_kwarg = 'topic'

    def get_queryset(self):
        return Questions.objects.prefetch_related(
                                    'answers').select_related(
                                                'quiz').filter(
                                                            quiz__title=self.kwargs['topic']).filter(
                                                                                       is_active=True)


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
    queryset = Answers.objects.select_related('question').only('id', 'text', 
                                                               'is_right', 'question__title').all()
    permission_classes = [IsAuthorOrReadOnly]


class AddAnswer(generics.CreateAPIView):
    serializer_class = SingleAnswerSerializer


class RegistrationAPI(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
