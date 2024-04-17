from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
import mailersend, json
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
from .models import Student
from .serializers import UserSerializer, StudentSerializer


def check_email_exists(self, email):
    User = get_user_model()
    return User.objects.filter(email=email).exists()


class signUp(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                print(serializer)
                email = serializer.validated_data.get('user', {}).get('email')
                print(email)

                user_data = serializer.validated_data.pop('user', {})
                print(user_data)

                user = User.objects.create_user(
                    username=user_data.get('username'),
                    email=email,
                    password=user_data.get('password'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    is_superuser=False,  # Assuming default value is False
                    is_staff=False,  # Assuming default value is False
                    is_active=False  # Assuming default value is False
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
