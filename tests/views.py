from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import Answer, Test, Question
from .serializers import TestSerializer, QuestionSerializer
from django.core.exceptions import ObjectDoesNotExist


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_test(request, module_id):
    professor = request.user

    # Ensure only professors can create tests
    if not professor.is_staff:
        return Response(
            {"error": "Você não tem permissão para criar testes."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = request.data
    test_data = data.get("test")
    questions_data = data.get("questions")

    if not test_data or not questions_data:
        return Response(
            {"error": "Dados do teste ou perguntas estão faltando."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Create the test
        test = Test.objects.create(
            module_id=module_id,
            name=test_data["name"],
            start_time=test_data["start_time"],
            end_time=test_data["end_time"],
            total_marks=int(test_data["total_marks"]),
        )

        # Create questions for the test
        for question_data in questions_data:
            Question.objects.create(
                test=test,
                question_type=question_data["tipo_de_pergunta"],
                text=question_data["texto"],
                option_a=question_data.get("opcao_a"),
                option_b=question_data.get("opcao_b"),
                option_c=question_data.get("opcao_c"),
                option_d=question_data.get("opcao_d"),
                correct_answer=question_data.get("resposta_correta"),
            )

        return Response(
            {"message": "Teste criado com sucesso!"}, status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Submit test answers
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_test_answers(request, test_id):
    student = request.user

    # Ensure only students can submit answers
    if student.is_staff:
        return Response(
            {"error": "Professors are not allowed to submit test answers."},
            status=status.HTTP_403_FORBIDDEN,
        )

    answers_data = request.data.get("answers")

    try:
        test = Test.objects.get(id=test_id)

        # Check if the test is active
        if not test.is_active():
            return Response(
                {"error": "Test is not active."}, status=status.HTTP_400_BAD_REQUEST
            )

        total_score = 0

        # Process answers
        for answer_data in answers_data:
            try:
                question = Question.objects.get(id=answer_data["question_id"])

                # Check if it's a multiple-choice question
                if question.question_type == "MCQ":
                    selected_option = answer_data.get("selected_option")
                    answer = Answer.objects.create(
                        student=student,
                        question=question,
                        selected_option=selected_option,
                    )
                    if answer.is_correct:
                        total_score += 1
                elif question.question_type == "TEXT":
                    text_answer = answer_data.get("text_answer")
                    Answer.objects.create(
                        student=student, question=question, text_answer=text_answer
                    )
            except ObjectDoesNotExist:
                return Response(
                    {
                        "error": f"Question with id {answer_data['question_id']} not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            {"message": "Answers submitted successfully!", "score": total_score},
            status=status.HTTP_200_OK,
        )

    except ObjectDoesNotExist:
        return Response({"error": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# View test results
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def view_test_results(request, test_id):
    student = request.user

    try:
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
                    "correct_answer": (
                        answer.question.correct_answer
                        if answer.question.question_type == "MCQ"
                        else None
                    ),
                }
                for answer in answers
            ],
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({"error": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
