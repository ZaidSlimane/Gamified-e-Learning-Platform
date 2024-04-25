from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import *

urlpatterns = [
    path('hello-world/', views.hello_world, name='hello_world'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('courses/', CourseListCreateAPIView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseRetrieveUpdateDestroyAPIView.as_view(), name='course-detail'),
    path('chapters/', ChapterListCreateAPIView.as_view(), name='chapter-list'),
    path('chapters/<int:pk>/', ChapterRetrieveUpdateDestroyAPIView.as_view(), name='chapter-detail'),
    path('courses/<int:course_id>/chapters/', CourseChapterListAPIView.as_view(), name='course-chapter-list'),
    path('courses/<int:course_id>/chapters/<int:pk>/', CourseChapterDetailAPIView.as_view(),
         name='course-chapter-detail'),
    path('courses/<int:course_id>/chapters/<int:pk>/delete/', CourseChapterDeleteAPIView.as_view(),
         name='course-chapter-delete'),
    path('delete/<int:pk>/', views.chapterdelete, name='delete-chapter'),

    path('enrollments/', EnrollmentListCreateAPIView.as_view(), name='enrollment-list-create'),
    path('enrollments/<int:pk>/', EnrollmentDetailAPIView.as_view(), name='enrollment-detail'),
    path('student/<int:student_id>/enrollments', EnrollmentByStudentAPIView.as_view(), name='enrollments-by-student'),
    path('course/<int:course_id>/enrollments', EnrollmentByCourseAPIView.as_view(), name='enrollments-by-course'),
    path('reviews/', ReviewListCreateAPIView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewDetailAPIView.as_view(), name='enrollment-detail'),
    path('course/<int:course_id>/reviews/', ReviewByCourseAPIView.as_view(), name='reviews-by-course'),
    path('student/<int:student_id>/reviews/', ReviewByStudentAPIView.as_view(), name='reviews-by-student'),
    path('questions/', QuestionListCreateAPIView.as_view(), name='question-list-create'),
    path('questions/<int:pk>/', QuestionRetrieveUpdateDestroyAPIView.as_view(),
         name='question-retrieve-update-destroy'),
    path('chapter/<int:chapter_id>/questions/', QuestionByChapterAPIView.as_view(), name='questions-by-chapter'),
    path('course/<int:course_id>/questions/', QuestionByCourseAPIView.as_view(), name='questions-by-course'),
    path('student/<int:student_id>/questions/', QuestionByStudentAPIView.as_view(), name='questions-by-student'),
    path('chat_participants/', ChatParticipantListCreateAPIView.as_view(), name='chat-participant-list-create'),
    path('chat_participants/<int:pk>/', ChatParticipantRetrieveUpdateDestroyAPIView.as_view(),
         name='chat-participant-retrieve-update-destroy'),
    path('chatrooms/', ChatroomListCreateAPIView.as_view(), name='chatroom-list-create'),
    path('chatrooms/<int:pk>/', ChatroomRetrieveUpdateDestroyAPIView.as_view(),
         name='chatroom-retrieve-update-destroy'),
    path('messages/', MessageListCreateAPIView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageRetrieveUpdateDestroyAPIView.as_view(), name='message-retrieve-update-destroy'),
    path('user/<int:user_id>/chatId', ChatParticipantByUserIDAPIView.as_view(),
         name='chat-participant-by-user'),
    path('chatParticipant/<int:participant_id>/chatrooms', ChatroomByChatParticipantAPIView.as_view(),
         name='chatroom-by-chatparticipant'),
    path('chatroom/<int:chatroom_id>/messages/', MessageByChatroomAPIView.as_view(), name='message-by-chatroom'),

]
