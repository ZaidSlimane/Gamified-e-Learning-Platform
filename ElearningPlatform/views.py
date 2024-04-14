from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
import mailersend, json
# Create your views here.
from .models import Student


def user_exists(email):
    return Student.user.objects.filter(email=email).exists()


def signUp(request):
    if request.method == 'POST':
        credentials = json.loads(request.body)

        try:
            if user_exists(credentials['email']):
                raise Exception('User exists')
            else:
                user = User.objects.create(
                    first_name=credentials['first_name'],
                    last_name=credentials['last_name'],
                    username=credentials['username'],
                    email=credentials['email'],
                    is_active=False,
                    is_staff=False,
                    is_superuser=False
                )

                # Create a new Student instance and associate it with the user
                student = Student(
                    user=user,
                    phone_number=credentials['phone_number'],
                    grade=credentials['grade']
                )

                return JsonResponse({'message': 'student created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
