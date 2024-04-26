from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
import mailersend, json
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from backend import settings
from .serializers import *
from .models import *
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.generics import ListCreateAPIView, DestroyAPIView

from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
from .models import Student
from .serializers import UserSerializer, StudentSerializer


def check_email_exists(self, email):
    User = get_user_model()
    return User.objects.filter(email=email).exists()


import logging
import random
import string
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Student
from .serializers import UserSerializer, StudentSerializer

logger = logging.getLogger(__name__)


def check_email_exists(email):
    return User.objects.filter(email=email).exists()


class signUp(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('user', {}).get('email')
                if check_email_exists(email):
                    raise ValidationError("The student is already registered")

                user_data = serializer.validated_data.pop('user', {})
                user = get_user_model().objects.create_user(
                    username=user_data.get('username'),
                    email=email,
                    password=user_data.get('password'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    is_superuser=False,
                    is_staff=False,
                    is_active=False
                )
                student_instance = Student(user=user,
                                           phone_number=serializer.validated_data.get('phone_number'),
                                           grade=serializer.validated_data.get('grade'),
                                           otp=serializer.validated_data.get('otp')
                                           )
                student_instance.save()
                request_code(request, student_instance)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def request_code(request, student_instance):
    try:
        code = generate_otp()
        student_instance.otp = code
        student_instance.save()
        send_verification_email(code, student_instance.user.email)
        return HttpResponse("Code sent! Please check your email.")
    except Exception as e:
        logger.error("Error sending verification email: %s", e)
        return HttpResponse("Failed to send verification code. Please try again later.")


def send_verification_email(code, email):
    try:
        subject = "Verification Code"
        message = f"Your verification code is: {code}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        email_message = EmailMessage(subject, message, from_email, to_email)
        email_message.content_subtype = "html"
        email_message.send()
    except Exception as e:
        logger.error("Error sending email: %s", e)
        raise


def generate_otp(length=4):
    return ''.join(random.choices(string.digits, k=length))


class verify(APIView):
    def post(self, request):
        user_code = request.POST.get('code', '')
        student = verify_student_code(user_code)
        if student:
            student.user.is_active = True
            student.user.save()
            student.otp = None
            student.save()
            return Response("Verified", status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error': 'The verification code you entered is invalid. Please try again.'},
                            status=status.HTTP_400_BAD_REQUEST)


def verify_student_code(user_code):
    try:
        Student.objects.get(otp=user_code)
        return True
    except Student.DoesNotExist as e:
        return False




@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello, world!'})


class home(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Welcome to the JWT Authentication page using React Js and Django!'}

        return Response(content)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."})
        except Exception as e:
            return Response({"error": "Invalid token or logout failed."}, status=400)


# Course views


class CourseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class ChapterListCreateAPIView(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


class ChapterRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


class CourseChapterListAPIView(ListCreateAPIView):
    serializer_class = ChapterSerializer

    def get_queryset(self):
        # Retrieve the course_id from the URL parameter
        course_id = self.kwargs['course_id']
        # Filter chapters based on the course_id
        return Chapter.objects.filter(course_id=course_id)


class CourseChapterDetailAPIView(RetrieveAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


class CourseChapterDeleteAPIView(DestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


@api_view(['DELETE'])
def chapterdelete(request, pk):
    try:
        chapter = Chapter.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    chapter.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class ChatroomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer


class ChatroomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer


class EnrollmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Enrollments.objects.all()
    serializer_class = EnrollmentsSerializer


class EnrollmentDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Enrollments.objects.all()
    serializer_class = EnrollmentsSerializer


class EnrollmentByCourseAPIView(generics.ListAPIView):
    serializer_class = EnrollmentsSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Enrollments.objects.filter(course_id=course_id)


class EnrollmentByStudentAPIView(generics.ListAPIView):
    serializer_class = EnrollmentsSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return Enrollments.objects.filter(student_id=student_id)


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewByCourseAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Review.objects.filter(enrollment__course_id=course_id)


class ReviewByStudentAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return Review.objects.filter(enrollment__student_id=student_id)


class QuestionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionByChapterAPIView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        chapter_id = self.kwargs['chapter_id']
        return Question.objects.filter(chapter_id=chapter_id)


class QuestionByCourseAPIView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Question.objects.filter(chapter__course_id=course_id)


class QuestionByStudentAPIView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return Question.objects.filter(student_id=student_id)


class ChatParticipantListCreateAPIView(generics.ListCreateAPIView):
    queryset = Chat_participant.objects.all()
    serializer_class = ChatParticipantSerializer


class ChatParticipantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat_participant.objects.all()
    serializer_class = ChatParticipantSerializer


class ChatroomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer


class ChatroomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chatroom.objects.all()
    serializer_class = ChatroomSerializer


class MessageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class MessageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class ChatParticipantByUserIDAPIView(generics.ListAPIView):
    serializer_class = ChatParticipantSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Chat_participant.objects.filter(student_id=user_id) | Chat_participant.objects.filter(teacher_id=user_id)


class ChatroomByChatParticipantAPIView(generics.ListAPIView):
    serializer_class = ChatroomSerializer

    def get_queryset(self):
        participant_id = self.kwargs['participant_id']
        return Chatroom.objects.filter(participants__id=participant_id)


class MessageByChatroomAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chatroom_id = self.kwargs['chatroom_id']
        return Message.objects.filter(room_id=chatroom_id)
