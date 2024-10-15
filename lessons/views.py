from rest_framework import generics, permissions
from .models import Content, Course, CourseProgress, Subject
from .serializers import CourseProgressSerializer, CourseSerializer
from rest_framework.response import Response
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)


# View to get courses associated with the authenticated user
class UserCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]  # Ensures the user is authenticated

    def get_queryset(self):
        # Print or log the authenticated user for debugging
        logging.debug(f"Authenticated User: {self.request.user}")
        print(f"Authenticated User: {self.request.user}")  # Debugging: Print user info

        # Filter courses by the logged-in user
        queryset = Course.objects.filter(owner=self.request.user)

        # Debugging: Print the queryset being returned
        logging.debug(f"Queryset: {queryset}")
        print(f"Queryset: {queryset}")

        return queryset

    def list(self, request, *args, **kwargs):
        # Print or log the request data for debugging
        logging.debug(f"Request Data: {request.data}")
        print(f"Request Data: {request.data}")  # Debugging: Print request data

        queryset = self.get_queryset()
        if not queryset.exists():
            logging.debug("No courses found for this user.")
            print("No courses found for this user.")  # Debugging: No courses found
            return Response({"error": "No courses found for this user."}, status=404)

        return super().list(request, *args, **kwargs)


from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)


from django.utils.text import slugify


class CreateCourseView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # To handle image uploads

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Usuário não autenticado"}, status=HTTP_403_FORBIDDEN
            )

        title = request.data.get("title")
        overview = request.data.get("overview")
        subject_title = request.data.get("subject_title")
        image = request.data.get("image")

        if not title or not overview or not subject_title:
            return Response(
                {"error": "Por favor, forneça todos os campos obrigatórios."},
                status=HTTP_400_BAD_REQUEST,
            )

        # Try to fetch or create the subject
        subject, created = Subject.objects.get_or_create(
            title=subject_title, defaults={"slug": slugify(subject_title)}
        )

        slug = slugify(title)
        course = Course.objects.create(
            owner=request.user,
            title=title,
            overview=overview,
            subject=subject,
            slug=slug,
            image=image,
        )
        return Response(CourseSerializer(course).data, status=HTTP_201_CREATED)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        subject_title = self.request.data.get("subject_title")
        if subject_title:
            subject, created = Subject.objects.get_or_create(title=subject_title)
            serializer.save(subject=subject)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            return Response(
                {"error": "Você não tem permissão para deletar este curso."},
                status=HTTP_403_FORBIDDEN,
            )
        instance.delete()


######################################################################################


class CourseProgressListCreateView(generics.ListCreateAPIView):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CourseProgress.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


# Retrieve, Update, and Delete Course Progress
class CourseProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CourseProgress.objects.filter(student=self.request.user)


# Mark content as completed
class MarkContentCompleteView(generics.UpdateAPIView):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        progress = self.get_object()
        content_id = kwargs.get("content_id")
        content = Content.objects.get(id=content_id)

        if content not in progress.completed_contents.all():
            progress.completed_contents.add(content)
            progress.save()

        return Response(self.get_serializer(progress).data)
