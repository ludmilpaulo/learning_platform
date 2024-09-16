from django.core.mail import send_mail
from django.contrib.auth.models import User

from rest_framework import serializers
from .models import StudentProfile, TutorProfile

from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', "password", "is_staff"]

        extra_kwargs = {'password': {'write_only': True}}

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = StudentProfile
        fields = '__all__'

class TutorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = TutorProfile
        fields = '__all__'

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    user_type = serializers.ChoiceField(choices=[('Tutor', 'Tutor'), ('Student', 'Student')])
    name = serializers.CharField(max_length=100)
    surname = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)
    id_number_or_passport = serializers.CharField(max_length=30)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')])
    date_of_birth = serializers.DateField()
    address = serializers.CharField()
    specialty = serializers.CharField(max_length=100, required=False)
    years_of_experience = serializers.IntegerField(required=False)
    documents = serializers.ListField(child=serializers.FileField(), required=False)

    def create(self, validated_data):
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'password': validated_data['password'],
        }
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        profile_data = {
            'user': user,
            'name': validated_data['name'],
            'surname': validated_data['surname'],
            'phone_number': validated_data['phone_number'],
            'id_number_or_passport': validated_data['id_number_or_passport'],
            'gender': validated_data['gender'],
            'date_of_birth': validated_data['date_of_birth'],
            'address': validated_data['address'],
        }

        if validated_data['user_type'] == 'Tutor':
            Tutor_data = {
                **profile_data,
                'specialty': validated_data['specialty'],
                'years_of_experience': validated_data['years_of_experience'],
                'consultation_category': validated_data['consultation_category'],
            }
            Tutor_serializer = TutorProfileSerializer(data=Tutor_data)
            Tutor_serializer.is_valid(raise_exception=True)
            Tutor_profile = Tutor_serializer.save()
            self.send_welcome_email(user, 'Tutor')
            return Tutor_profile

        Student_serializer = StudentProfileSerializer(data=profile_data)
        Student_serializer.is_valid(raise_exception=True)
        Student_profile = Student_serializer.save()
        self.send_welcome_email(user, 'Student')
        return Student_profile

    def send_welcome_email(self, user, user_type):

        if user_type == 'Tutor':
            subject = 'Welcome to the learning Platform'
            message = (
                'Dear Tutor, welcome to our platform. Your account will be activated in 78 hours pending background checks. '
                'If you have any other supported documents, please respond to this email with the attached documents.'
            )
        else:
            subject = 'Welcome to the learning Platform'
            message = 'Dear student, welcome to our platform.'
        send_mail(subject, message, 'from@example.com', [user.email])

    def validate(self, data):
        if data['user_type'] == 'Tutor':
            if not data.get('specialty') or not data.get('years_of_experience') or not data.get('consultation_category'):
                raise serializers.ValidationError('Tutors must provide specialty, years of experience, and consultation category.')
        return data






###############################################################

