from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    ),
    grade = models.fields.CharField(max_length=20),
    points = models.fields.IntegerField()


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    ),
    grade = models.fields.CharField(max_length=50),
    institute = models.fields.CharField(max_length=100)


class Course(models.Model):
    courseName = models.CharField(max_length=100)
    courseSummary = models.TextField(max_length=100)
    recompense = models.fields.IntegerField()
    terms = models.fields.CharField(max_length=255)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)


class Chapter (models.Model):
    chapterName = models.CharField(max_length=100)
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

