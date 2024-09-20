from rest_framework import serializers
from .models import Test, Question, Answer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_type', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'name', 'start_time', 'end_time', 'total_marks', 'questions']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'student', 'question', 'selected_option', 'text_answer', 'is_correct']
