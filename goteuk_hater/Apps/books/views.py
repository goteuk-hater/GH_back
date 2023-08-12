from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import BookCategory, Book
from .serializer import BookCategorySerializer, BookSerializer
from rest_framework import status

class CategoryListGetAPI(APIView):
    def get(self, request, format=None):
        rq = BookCategory.objects.all()
        serializer = BookCategorySerializer(rq, many=True)
        return Response({'data': serializer.data})

class BookListCreateAPI(APIView):
    def get(self, request, format=None):
        rq = Book.objects.all()
        if not rq:
            return Response({'detail': 'No data'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSerializer(rq, many=True)
        return Response({'data': serializer.data})
    
    def post(self, request, format=None):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, format=None):
        # BookCategory 테이블의 모든 내용 삭제
        delete_book = Book.objects.all().delete()
        if delete_book:
            return Response({'detail': 'All categories deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'No categories to delete'}, status=status.HTTP_404_NOT_FOUND)


