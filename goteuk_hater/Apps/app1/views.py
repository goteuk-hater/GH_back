from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from Apps.app1.serializers import StudentSerializer
from .models import Student

class StudentListCreateAPIView(ListCreateAPIView):
	serializer_class = StudentSerializer
	queryset = Student.objects.all()
	
class StudentRetrieveUpdateDestroyAPIVIew(RetrieveUpdateDestroyAPIView):
	serializer_class = StudentSerializer
	queryset = Student.objects.all()
	lookup_url_kwarg = 'student_pk'
