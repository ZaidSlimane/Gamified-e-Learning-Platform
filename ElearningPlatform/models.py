from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        unique=True,
    )
    phone_number = models.CharField(max_length=20)
    grade = models.fields.CharField(max_length=20)
    points = models.fields.IntegerField(default=0)
    otp = models.fields.CharField(blank=True, default=None, max_length=6, null=True)

    def __str__(self):
        return self.user.username


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        unique=True,
    )
    grade = models.CharField(max_length=50)
    institute = models.CharField(max_length=100)


class Course(models.Model):
    courseName = models.CharField(max_length=100)
    courseSummary = models.TextField(max_length=500)
    recompense = models.fields.IntegerField()
    terms = models.fields.CharField(max_length=255)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    imglink = models.TextField(max_length=100)
    courseLongSummary = models.TextField(max_length=500)


class Games(models.Model):
    game_name = models.CharField(max_length=100)
    game_points = models.IntegerField()
    question_text = models.CharField(max_length=255)
    answer1_text = models.CharField(max_length=255)
    answer2_text = models.CharField(max_length=255)
    answer3_text = models.CharField(max_length=255)
    correct_answer = models.IntegerField(choices=[(1, 'Answer 1'), (2, 'Answer 2'), (3, 'Answer 3')])

class Chapter(models.Model):
    chapterName = models.CharField(max_length=100)
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    game = models.ForeignKey(Games, on_delete=models.CASCADE)


class Enrollments(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    passed_chapter = models.IntegerField(default=0)


class Review(models.Model):
    review_content = models.TextField()
    stars = models.IntegerField()
    enrollment = models.ForeignKey(Enrollments, on_delete=models.CASCADE)


class Question(models.Model):
    question_content = models.TextField()
    question_answer = models.TextField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)





class Chat_participant(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

class Chatroom(models.Model):
    room_name = models.CharField(max_length=100)
    participants = models.ManyToManyField(Chat_participant)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Message(models.Model):
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    sender = models.ForeignKey(Chat_participant, on_delete=models.CASCADE, default=None)
