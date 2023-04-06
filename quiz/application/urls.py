from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .views import *


urlpatterns = [
    path('', api_root, name='root'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('category/<int:pk>/', CategoryDetail.as_view(), name='category'),
    path('quizzes/', QuizList.as_view(), name='quizzes'),
    path('quiz/<int:pk>/', QuizDetail.as_view(), name='quiz'),
    path('questions/', QuizQuestions.as_view(), name='questions'),
    path('question/<int:pk>/', QuestionDetail.as_view(), name='question'),
    path('random/', RandomQuestion.as_view(), name='random'),
    path('answer/<int:pk>/', AnswerDetail.as_view(), name='answer'),
    path('add-answer/', AddAnswer.as_view(), name='add_answer'),
]
