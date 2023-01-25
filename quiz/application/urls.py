from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


urlpatterns = [
    path('', api_root, name='root'),
    path('register/', RegistrationAPI.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('category/<int:pk>', CategoryDetail.as_view(), name='category'),
    path('quizzes/', QuizList.as_view(), name='quizzes'),
    path('quiz/<int:pk>', QuizDetail.as_view(), name='quiz'),
    path('questions/<str:topic>', QuizQuestions.as_view(), name='questions'),
    path('question/<int:pk>', QuestionDetail.as_view(), name='question'),
    path('random/<str:topic>', RandomQuestion.as_view(), name='random'),
    path('answer/<int:pk>', AnswerDetail.as_view(), name='answer'),
    path('add-answer/', AddAnswer.as_view(), name='add_answer'),
]
