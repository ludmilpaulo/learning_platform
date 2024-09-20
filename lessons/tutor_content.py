from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .models import Content, Module, Text, Image, Video, File
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])  # Allow anyone to access this view
def create_content(request, module_id):
    """
    Function-based view to create content for a specific module.
    Token is extracted from the request body.
    """
    data = request.data

    # Try to fetch the token from the request body and authenticate the user
    try:
        token_key = data["token"]
        logger.info(f"Received token: {token_key}")  # Log the received token
        user = Token.objects.get(key=token_key).user
        logger.info(f"Authenticated user: {user.username}")  # Log the authenticated user
    except KeyError:
        logger.error("Token ausente no corpo da solicitação.")
        return Response(
            {"status": "failed", "error": "Token de acesso ausente."},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Token.DoesNotExist:
        logger.error(f"Token inválido: {token_key}")
        return Response(
            {"status": "failed", "error": "Token de acesso inválido."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Validate the module exists
    try:
        module = Module.objects.get(pk=module_id)
    except Module.DoesNotExist:
        return Response(
            {'detail': 'Módulo não encontrado.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Skip ownership check if you want to allow all users to create content
    # Check if the user is the owner of the course (optional, you can remove this check)
    if module.course.owner != user:
        return Response(
            {'detail': 'Você não tem permissão para adicionar conteúdo a este módulo.'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Extract and validate the content type
    content_type_name = request.data.get('content_type')
    if not content_type_name:
        return Response(
            {'detail': 'O tipo de conteúdo é obrigatório.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Try to fetch the content type
    try:
        content_type = ContentType.objects.get(model=content_type_name.lower())
    except ContentType.DoesNotExist:
        return Response(
            {'detail': 'Tipo de conteúdo inválido.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Process the content based on the type
    if content_type_name == 'text':
        content = request.data.get('content')
        if not content:
            return Response(
                {'detail': 'O conteúdo de texto é obrigatório.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        text_content = Text.objects.create(
            owner=user,
            title=request.data.get('title', 'Conteúdo de Texto'),
            content=content
        )
        Content.objects.create(module=module, content_type=content_type, object_id=text_content.id)

    elif content_type_name == 'video':
        url = request.data.get('url')
        if not url:
            return Response(
                {'detail': 'O URL do vídeo é obrigatório.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        video_content = Video.objects.create(
            owner=user,
            title=request.data.get('title', 'Conteúdo de Vídeo'),
            url=url
        )
        Content.objects.create(module=module, content_type=content_type, object_id=video_content.id)

    elif content_type_name == 'image':
        if 'file' not in request.FILES:
            return Response(
                {'detail': 'O arquivo de imagem é obrigatório.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        image_content = Image.objects.create(
            owner=user,
            title=request.data.get('title', 'Conteúdo de Imagem'),
            file=request.FILES['file']
        )
        Content.objects.create(module=module, content_type=content_type, object_id=image_content.id)

    elif content_type_name == 'file':
        if 'file' not in request.FILES:
            return Response(
                {'detail': 'O arquivo é obrigatório.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        file_content = File.objects.create(
            owner=user,
            title=request.data.get('title', 'Conteúdo de Arquivo'),
            file=request.FILES['file']
        )
        Content.objects.create(module=module, content_type=content_type, object_id=file_content.id)

    else:
        return Response(
            {'detail': 'Tipo de conteúdo não suportado.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({'detail': 'Conteúdo criado com sucesso!'}, status=status.HTTP_201_CREATED)
