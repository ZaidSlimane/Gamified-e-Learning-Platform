from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from backend import settings
from .serializers import *
from .models import *
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.decorators import api_view
import logging
import random
import string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Student
from .serializers import UserSerializer, StudentSerializer

logger = logging.getLogger(__name__)


# Create your views here.

class signUp(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                user_data = serializer.validated_data.pop('user', {})
                email = user_data.get('email')
                if check_email_exists(email):
                    raise ValidationError("The student is already registered")
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
                                           )
                student_instance.save()

                # request_code(student_instance)
                # You should return a success response here, such as:
                return HttpResponse("Code sent! Please check your email.")
            else:
                # The errors should be returned here in the else block.
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def request_code(student_instance):
    try:
        code = generate_otp()
        # Verifing the email is sent first
        send_verification_email(code, student_instance.user.email)
        # Save the otp in the student
        student_instance.otp = code
        student_instance.save()
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
        delete_user(email)
        logger.error("Error sending email: %s", e)
        raise


def delete_user(email):
    try:
        # Get the user with the specified email address
        user = User.objects.get(email=email)
        user.delete()
    except ObjectDoesNotExist as e:
        # User with the specified email address does not exist
        logger.error("User could not be deleted", e)


def check_email_exists(email):
    return User.objects.filter(email=email).exists()


def generate_otp(length=4):
    return ''.join(random.choices(string.digits, k=length))


class verify(APIView):
    def post(self, request):
        user_code = request.data.get('code')
        print(user_code)
        student = verify_student_code(user_code)
        if student:

            # Add the student in the student group
            student_group = Group.objects.get(name='STUDENT')
            student_group.user_set.add(student.user)

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
        return Student.objects.get(otp=user_code)
    except Student.DoesNotExist as e:
        logger.error(e)
        return None


@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello, world!'})


class home(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_group = get_user_group(user)

        if user_group == "STUDENT":
            student = Student.objects.get(user=user)
            serializer = StudentSerializer(student)
            serialized_data = serializer.data
            return Response(serialized_data)
        else:
            return JsonResponse({'error': 'User is not a student.'}, status=400)


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = User.objects.get(username=username)
        if not user.groups.filter(name='STUDENT').exists():
            return Response({'detail': 'Only STUDENT group users can log in.'}, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenObtainPairSerializer(data={'username': username, 'password': password})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_user_group(user):
    try:
        group = user.groups.first()
        return group.name
    except Exception as e:
        logger.error(e)
        return None


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

    def perform_create(self, serializer):
        teacher_id = self.request.data.get('teacher')  # Assuming 'teacher' is the key for teacher ID in request data
        serializer.save(teacher_id=teacher_id)


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


class EnrollmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollments.objects.all()
    serializer_class = EnrollmentsSerializer

    def perform_update(self, serializer):
        serializer.save()


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

class NotEnrolledCoursesByStudentAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer  # Assuming you have a serializer for courses

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        all_courses = Course.objects.all()
        enrolled_courses = Enrollments.objects.filter(student_id=student_id).values_list('course_id', flat=True)
        not_enrolled_courses = all_courses.exclude(id__in=enrolled_courses)
        return not_enrolled_courses


class EnrolledCoursesByStudentAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer  # Assuming you have a serializer for courses

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        # Get the IDs of courses in which the student is enrolled
        enrolled_course_ids = Enrollments.objects.filter(student_id=student_id).values_list('course_id', flat=True)
        # Get the courses that match these IDs
        enrolled_courses = Course.objects.filter(id__in=enrolled_course_ids)
        return enrolled_courses




class EnrollmentByStudentAndCourseAPIView(generics.ListAPIView):
    serializer_class = EnrollmentsSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        course_id = self.kwargs['course_id']
        return Enrollments.objects.filter(student_id=student_id, course_id=course_id)


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class TeacherListCreateAPIView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TeacherDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


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



class AnsweredQuestionListAPIView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.exclude(question_answer='no answer yet')

class UnansweredQuestionListAPIView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(question_answer='no answer yet')



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



class GameListCreateAPIView(generics.ListCreateAPIView):
    queryset = Games.objects.all()
    serializer_class = GamesSerializer


class GameDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Games.objects.all()
    serializer_class = GamesSerializer


class GameByChapterAPIView(generics.ListAPIView):
    serializer_class = GamesSerializer

    def get_queryset(self):
        chapter_id = self.kwargs.get('chapter_id')
        return Games.objects.filter(chapter_id=chapter_id)


class StatisticsListCreateAPIView(generics.ListCreateAPIView):
    queryset = statistics.objects.all()
    serializer_class = StatisticsSerializer

class StatisticsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = statistics.objects.all()
    serializer_class = StatisticsSerializer
    def perform_update(self, serializer):
        serializer.save()


class StatisticsByEnrollmentListAPIView(generics.ListAPIView):
    serializer_class = StatisticsSerializer

    def get_queryset(self):
        enrollment_id = self.kwargs['enrollment_id']
        return statistics.objects.filter(enrollment_id=enrollment_id)

class StatisticsByDateListAPIView(generics.ListAPIView):
    serializer_class = StatisticsSerializer

    def get_queryset(self):
        date = self.kwargs['date']
        return statistics.objects.filter(date=date)

class StatisticsByEnrollmentAndDateListAPIView(generics.ListAPIView):
    serializer_class = StatisticsSerializer

    def get_queryset(self):
        enrollment_id = self.kwargs['enrollment_id']
        date = self.kwargs['date']
        return statistics.objects.filter(enrollment_id=enrollment_id, date=date)

class StatisticsByStudentListAPIView(generics.ListAPIView):
    serializer_class = StatisticsSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return statistics.objects.filter(enrollment__student_id=student_id)
class StatisticsByCourseAndStudentListAPIView(generics.ListAPIView):
    serializer_class = StatisticsSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        student_id = self.kwargs['student_id']
        return statistics.objects.filter(enrollment__course_id=course_id, enrollment__student_id=student_id)
