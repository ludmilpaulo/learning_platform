from rest_framework import permissions, status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from .models import Module, Text, Video, Image, File, Content
from .serializers import ContentSerializer


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_content(request, content_id):
    """
    Deletes a specific content by its ID.
    """
    try:
        token_key = request.data.get("token")
        user = Token.objects.get(key=token_key).user
    except KeyError:
        return Response({"error": "Token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
    except Token.DoesNotExist:
        return Response({"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        content = Content.objects.get(pk=content_id)
        if content.module.course.owner != user:
            return Response(
                {"error": "You don't have permission to delete this content."},
                status=status.HTTP_403_FORBIDDEN,
            )
        content.delete()
        return Response({"message": "Content deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Content.DoesNotExist:
        return Response({"error": "Content not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PUT"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def edit_content(request, content_id):
    """
    Edits a specific content by its ID.
    """
    try:
        token_key = request.data.get("token")
        user = Token.objects.get(key=token_key).user
    except KeyError:
        return Response({"error": "Token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
    except Token.DoesNotExist:
        return Response({"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        content = Content.objects.get(pk=content_id)
        if content.module.course.owner != user:
            return Response(
                {"error": "You don't have permission to edit this content."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update content based on type
        if content.content_type.model == "text":
            content_data = content.content_object
            content_data.content = request.data.get("content", content_data.content)
            content_data.save()
        elif content.content_type.model == "video":
            content_data = content.content_object
            content_data.url = request.data.get("url", content_data.url)
            content_data.save()
        elif content.content_type.model == "image" and "file" in request.FILES:
            content_data = content.content_object
            content_data.file = request.FILES["file"]
            content_data.save()
        elif content.content_type.model == "file" and "file" in request.FILES:
            content_data = content.content_object
            content_data.file = request.FILES["file"]
            content_data.save()
        else:
            return Response(
                {"error": "Invalid or unsupported content type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Content updated successfully."}, status=status.HTTP_200_OK)
    except Content.DoesNotExist:
        return Response({"error": "Content not found."}, status=status.HTTP_404_NOT_FOUND)
