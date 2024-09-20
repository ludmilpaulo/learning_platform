from django.views.decorators.csrf import csrf_exempt
from accounts.models import StudentProfile
from learning_platform import settings
from lessons.models import Course, CourseProgress
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def enroll_user(request):
    data = request.data
    email = data.get('email')
    name = data.get('name')
    surname = data.get('surname')
    phone_number = data.get('phone_number')
    date_of_birth = data.get('date_of_birth')
    course_id = data.get('course_id')

    try:
        # Parse date of birth to be part of the password
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").strftime("%Y%m%d")
    except ValueError:
        return Response({'detail': 'Data de nascimento inválida.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a custom password using the surname, date_of_birth, and phone_number
    password = f"{surname}{dob}{phone_number}"

    # Check if the user already exists
    user, created = User.objects.get_or_create(
        username=email,
        email=email,
        defaults={'first_name': name, 'last_name': surname}
    )

    if created:
        # Set the password for the user
        user.set_password(password)
        user.save()

    # Get or create the student profile
    profile, _ = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            'name': name,
            'surname': surname,
            'phone_number': phone_number,
            'id_number_or_passport': data.get('id_number_or_passport', ''),
            'gender': data.get('gender', ''),
            'date_of_birth': date_of_birth,
            'address': data.get('address', ''),
        }
    )

    # Check if the course exists
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'detail': 'Curso não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user is already enrolled in the course
    if course.students.filter(id=user.id).exists():
        progress = CourseProgress.objects.filter(student=user, course=course).first()
        if progress and progress.get_progress_percentage() >= 100:
            return Response({'detail': 'Você já completou este curso.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Você já está inscrito neste curso.'}, status=status.HTTP_400_BAD_REQUEST)

    # Enroll the user in the course
    course.students.add(user)

    # Generate or retrieve the authentication token
    token, _ = Token.objects.get_or_create(user=user)

    # Send a welcome email with login credentials
    instructor_name = course.owner.get_full_name() or course.owner.username
    course_name = course.title
    subject = f"Bem-vindo ao curso {course_name}!"
    login_url = "{settings.FRONTEND_URL}/Login"  # Change to your actual login URL

    # Render the HTML email content
    html_content = render_to_string('emails/welcome.html', {
        'name': name,
        'course_name': course_name,
        'instructor_name': instructor_name,
        'email': email,
        'password': password,
        'login_url': login_url,
    })

    # Create the email message
    email_message = EmailMultiAlternatives(
        subject=subject,
        body='Bem-vindo ao curso!',  # Fallback plain-text message
        from_email=settings.EMAIL_HOST_USER,
        to=[email]
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()

    return Response({
        'detail': 'Inscrição realizada com sucesso!',
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser
    }, status=status.HTTP_201_CREATED)
