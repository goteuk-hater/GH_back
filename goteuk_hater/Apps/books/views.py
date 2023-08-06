from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BookCategory, Book
from .serializer import BookCategorySerializer, BookSerializer
from rest_framework import status

@api_view(['GET'])
def get_list_all(request):
    if request.method == 'GET':
        rq = BookCategory.objects.all()
        serializer = BookCategorySerializer(rq, many=True)
        return Response({'data': serializer.data})
    return Response({'message: You can only "GET" requests'})

@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        rq = Book.objects.all()
        if not rq:
            return Response({'detail: No data'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSerializer(rq, many=True)
            
        return Response({'data': serializer.data})
    
    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=404)


