from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Quizzes, Questions, Answers, Categories
from django.http import Http404
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Categories
        fields = ('id', 'name')


class QuizSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')

    class Meta:
        model = Quizzes
        fields = ('id', 'title', 'category')

    def create(self, validated_data):
        category_name = validated_data['category']['name']
        if Categories.objects.filter(name=category_name).exists():
            category = Categories.objects.get(name=category_name)
        else:
            category = Categories.objects.create(name=category_name)
        return Quizzes.objects.create(title=validated_data['title'], category=category)

    def update(self, instance, validated_data):
        category_name = validated_data['category']['name']
        if Categories.objects.filter(name=category_name).exists():
            category = Categories.objects.get(name=category_name)
        else:
            category = Categories.objects.create(name=category_name)
        instance.title = validated_data.get('title', instance.title)
        instance.category = category
        instance.save()
        return instance


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answers
        fields = ('id', 'text', 'is_right')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    quiz = serializers.CharField(source='quiz.title')


    class Meta:
        model = Questions
        fields = ('quiz', 'title', 'id', 'kind', 'difficulty',
                  'is_active', 'answers')

    def create(self, validated_data):
        quiz_name = validated_data['quiz']['title']
        if Quizzes.objects.filter(title=quiz_name).exists():
            validated_data['quiz'] = Quizzes.objects.get(title=quiz_name)
            return Questions.objects.create(**validated_data)
        raise Http404

    def update(self, instance, validated_data):
        quiz_name = validated_data['quiz']['title']
        if Quizzes.objects.filter(title=quiz_name).exists():
            validated_data['quiz'] = Quizzes.objects.get(title=quiz_name)
            instance.quiz = validated_data.get('quiz', instance.quiz)
            instance.title = validated_data.get('title', instance.title)
            instance.kind = validated_data.get('kind', instance.kind)
            instance.difficulty = validated_data.get('difficulty', instance.difficulty)
            instance.is_active = validated_data.get('is_active', instance.is_active)
            instance.save()
            return instance
        raise Http404


class SingleAnswerSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='question.title')

    class Meta:
        model = Answers
        fields = ('question', 'id', 'text', 'is_right')

    def update(self, instance, validated_data):
        question_name = validated_data['question']['title']
        if Questions.objects.filter(title=question_name).exists():
            validated_data['question'] = Questions.objects.get(title=question_name)
            instance.question = validated_data.get('question', instance.question)
            instance.text = validated_data.get('text', instance.text)
            instance.is_right = validated_data.get('is_right', instance.is_right)
            instance.save()
            return instance
        raise Http404

    def create(self, validated_data):
        question_name = validated_data['question']['title']
        if Questions.objects.filter(title=question_name).exists():
            validated_data['question'] = Questions.objects.get(title=question_name)
            return Answers.objects.create(**validated_data)
        raise Http404


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


    def validate(self, validated_data):
        if validated_data['password'] != validated_data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return validated_data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
