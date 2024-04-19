import hashlib
import logging
import os
from datetime import datetime

from django.utils import timezone
from email.message import EmailMessage

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import get_connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
import mailersend, json
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.conf import settings
import random
from backend import settings

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

logger = logging.getLogger(__name__)


def check_email_exists(email):
    return User.objects.filter(email=email).exists()


class signUp(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                print(serializer)
                email = serializer.validated_data.get('user', {}).get('email')
                print(email)

                if check_email_exists(email):
                    raise ValidationError("The Student is already registered")
                else:
                    user_data = serializer.validated_data.pop('user', {})
                    print(user_data)

                    # Request a code to verify the student email

                    request_code(request, email)
                    redirect('verify')

                    user = User.objects.create_user(
                        username=user_data.get('username'),
                        email=email,
                        password=user_data.get('password'),
                        first_name=user_data.get('first_name'),
                        last_name=user_data.get('last_name'),
                        is_superuser=False,  # Assuming default value is False
                        is_staff=False,  # Assuming default value is False
                        is_active=True  # Assuming default value is False
                    )
                print(user)
                student_instance = Student(user=user,
                                           phone_number=serializer.validated_data.get('phone_number'),
                                           grade=serializer.validated_data.get('grade')
                                           )
                student_instance.save()

                return Response(status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def request_code(request, email):
    try:
        code = get_random_code()
        hashed_code = hashlib.sha256(str(code).encode()).hexdigest()
        request.session['verification_code'] = hashed_code
        send_verification_email(code, email)
        request.session['verification_start_time'] = datetime.now()
        return HttpResponse("Code sent! Please check your email.")
    except Exception as e:
        logger.error("Error sending verification email: %s", e)
        return HttpResponse("Failed to send verification code. Please try again later.")


def send_verification_email(code, email):
    try:
        subject = "Verification Code"
        message = f"Your verification code is: {code}"
        from_email = "MS_Qk56Qv@trial-pq3enl6yr85g2vwr.mlsender.net"
        recipient_list = [email]

        connection = get_connection(
            host=settings.MAILERSEND_SMTP_HOST,
            port=settings.MAILERSEND_SMTP_PORT,
            username=settings.MAILERSEND_SMTP_USERNAME,
            password=settings.MAILERSEND_SMTP_PASSWORD,
            use_tls=True,
        )

        email = EmailMessage(subject, message, from_email, recipient_list, connection=connection)
        email.content_subtype = "html"
        email.send()
    except Exception as e:
        logger.error("Error sending email: %s", e)
        raise


def get_random_code():
    return random.randint(1000, 9999)


class verify(APIView):
    def post(self, request):
        user_code = request.POST.get('code', '')
        verification_code = request.session.get('verification_code')
        verification_start_time = request.session.get('verification_start_time')
        total_waiting_time = (timezone.now() - verification_start_time).total_seconds()

        if not verification_code or not verification_start_time or total_waiting_time >= 5 * 60:
            return HttpResponse("The verification session has expired. Please request a new code.")

        if user_code == verification_code:
            del request.session['verification_code']
            del request.session['verification_start_time']
            return redirect('signUp')
            return HttpResponse("Code verified successfully!")
        else:
            return HttpResponse("Invalid code. Please retry.")


@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello, world!'})


class Login(APIView):
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