from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Quizzes, Questions, Answers, Categories
from django.http import Http404
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для обработки
    CRUD операций с категориями
    """
    # Автор - по умолчанию пользователь, который делает запрос
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    author_name = serializers.StringRelatedField(
        source='author',
        read_only=True)

    class Meta:
        model = Categories
        fields = ('id', 'name', 'author', 'author_name')


class QuizSerializer(serializers.ModelSerializer):
    """
    Обрабатывает создание, обновление
    удаление, получение квиза, а также
    получения списка квизов
    """
    title = serializers.CharField(
        required=True
    )
    category = serializers.CharField(
        source='category.name')
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    author_name = serializers.StringRelatedField(
        source='author',
        read_only=True)

    class Meta:
        model = Quizzes
        fields = ('id', 'title', 'category',
                  'author', 'author_name')

    def create(self, validated_data):
        category_name = validated_data['category']['name']
        # Если категория есть, выбираю её, если нет - создаю новую
        if Categories.objects.filter(name=category_name).exists():
            category = Categories.objects.get(name=category_name)
        else:
            category = Categories.objects.create(name=category_name,
                                                 author=validated_data['author'])
        return Quizzes.objects.create(title=validated_data['title'], category=category,
                                      author=validated_data['author'])

    def update(self, instance, validated_data):
        category_name = validated_data['category']['name']
        if Categories.objects.filter(name=category_name).exists():
            category = Categories.objects.get(name=category_name)
        else:
            category = Categories.objects.create(name=category_name,
                                                 author=validated_data['author'])
        instance.title = validated_data.get('title', instance.title)
        instance.category = category
        instance.save()
        return instance


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answers
        fields = ('id', 'text', 'is_right')


class QuestionSerializer(serializers.ModelSerializer):
    # конвертирует вопрос/все вопросы и для каждого из них все возможные ответы
    # Конвертирует рандомный вопрос и все возможные ответы для него
    # answers = serializers.StringRelatedField(many=True)
    # answers = serializers.PrimaryKeyRelatedField(many=True, queryset = Answers.objects.all())
    # Отвечает за отображение первичных ключей записей связанной модели, хоть в Queryset
    # выбираются все, но скорее всего во view под капотом происходит фильтрация данных связ. модели
    answers = AnswerSerializer(many=True, read_only=True)
    # соответствует question.answers (отфильтрованные,
    # т.е соответсвующие конкретной записи (question)), передаётся в сериализатор
    quiz = serializers.CharField(source='quiz.title')
    # можно указать и id
    # если используется values, то нужно явно указывать поле, на которое ссылаюсь как выше category__name
    # без values можно указать атрибут через точку

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
    # Если values не используется то, атрибут вторичной модели указывается
    # через точку, иначе, через двойное подчеркивание
    # если в only передать с двойным подчеркиванием, то можно указать через точку также здесь

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
    """
    Сериализатор для обработки созжания пользователей
    """

    # добавляю валидатор уникальности почты и флаг
    # обязательно для заполнения
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    # Добавляю валидатор проверки пароля
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, validated_data):
        """
        Доп. валидация для проверки совпадения паролей
        """
        if validated_data['password'] != validated_data['password2']:
            raise serializers.ValidationError({"password, password2":
                                               "Password fields didn't match."})
        return validated_data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        # пароль хешируется и устанавливается
        user.save()
        return user
