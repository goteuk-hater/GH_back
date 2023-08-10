from django.urls import path

from .views import StudentListCreateAPIView, StudentRetrieveUpdateDestroyAPIVIew

urlpatterns = [
    path('student/', StudentListCreateAPIView.as_view()),
    path('student/<student_pk>', StudentRetrieveUpdateDestroyAPIVIew.as_view())
]