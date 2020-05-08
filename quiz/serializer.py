from rest_framework import serializers

from .models import Quiz, Question


class QuzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'user']


class QuestionSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question', 'option1', 'option2', 'option3', 'option4', 'answer', 'quiz']
