from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Student
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Teacher
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_instance, _ = User.objects.get_or_create(**user_data)
        teacher_instance = Teacher.objects.create(user=user_instance, **validated_data)
        return teacher_instance




class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'courseName', 'courseSummary','courseLongSummary', 'recompense', 'terms', 'teacher', 'imglink']
        read_only_fields = ['teacher']

    def create(self, validated_data):
        teacher_id = self.context.get('request').data.get('teacher')  # Assuming 'teacher' is the key for teacher ID in request data
        validated_data['teacher_id'] = teacher_id
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request.method == 'GET':
            data['teacher_id'] = instance.teacher_id
        return data

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'




class EnrollmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollments
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow partial updates
        self.partial = True



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class GamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = '__all__'

class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = statistics
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow partial updates
        self.partial = True


class ChatParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_participant
        fields = '__all__'


class ChatroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatroom
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
