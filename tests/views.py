from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import Answer, Test, Question
from .serializers import TestSerializer, QuestionSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_test(request, module_id):
    professor = request.user
    data = request.data
    test_data = data.get('test')
    questions_data = data.get('questions')

    test = Test.objects.create(
        module_id=module_id,
        name=test_data['name'],
        start_time=test_data['start_time'],
        end_time=test_data['end_time'],
        total_marks=test_data['total_marks']
    )

    for question_data in questions_data:
        question = Question.objects.create(
            test=test,
            question_type=question_data['question_type'],
            text=question_data['text'],
            option_a=question_data.get('option_a'),
            option_b=question_data.get('option_b'),
            option_c=question_data.get('option_c'),
            option_d=question_data.get('option_d'),
            correct_answer=question_data.get('correct_answer')
        )
    
    return Response({"message": "Test created successfully!"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_test_answers(request, test_id):
    student = request.user
    answers_data = request.data.get('answers')
    test = Test.objects.get(id=test_id)

    if not test.is_active():
        return Response({"error": "Test is not active."}, status=status.HTTP_400_BAD_REQUEST)

    total_score = 0
    for answer_data in answers_data:
        question = Question.objects.get(id=answer_data['question_id'])

        if question.question_type == 'MCQ':
            selected_option = answer_data.get('selected_option')
            answer = Answer.objects.create(
                student=student,
                question=question,
                selected_option=selected_option
            )
            if answer.is_correct:
                total_score += 1
        elif question.question_type == 'TEXT':
            text_answer = answer_data.get('text_answer')
            Answer.objects.create(
                student=student,
                question=question,
                text_answer=text_answer
            )

    return Response({"message": "Answers submitted successfully!", "score": total_score}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def view_test_results(request, test_id):
    student = request.user
    test = Test.objects.get(id=test_id)
    answers = Answer.objects.filter(student=student, question__test=test)

    response_data = {
        "test": test.name,
        "score": sum(1 for answer in answers if answer.is_correct),
        "total_questions": test.questions.count(),
        "answers": [
            {
                "question": answer.question.text,
                "selected_option": answer.selected_option,
                "text_answer": answer.text_answer,
                "is_correct": answer.is_correct,
                "correct_answer": answer.question.correct_answer if answer.question.question_type == 'MCQ' else None
            }
            for answer in answers
        ]
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

