from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from lessons.models import Module, Content
from lessons.serializers import ContentSerializer
from rest_framework.exceptions import PermissionDenied


@api_view(["POST"])
@permission_classes([permissions.AllowAny])  # Manually authenticate using the token
def get_module_contents(request, module_id):
    data = request.data

    # Try to fetch the token from the request body
    try:
        token_key = data["token"]
        user = Token.objects.get(key=token_key).user
    except (KeyError, Token.DoesNotExist):
        return Response(
            {"error": "Token inválido ou ausente."}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Fetch the module and course
    try:
        module = Module.objects.get(id=module_id)
    except Module.DoesNotExist:
        return Response(
            {"error": "Módulo não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )

    # Check if the user is the course owner or a student in the course
    if (
        module.course.owner != user
        and not module.course.students.filter(id=user.id).exists()
    ):
        raise PermissionDenied(
            "Você não tem permissão para visualizar o conteúdo deste módulo."
        )

    # Fetch the contents related to the module
    contents = Content.objects.filter(module=module)

    # Serialize the contents
    serializer = ContentSerializer(contents, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
