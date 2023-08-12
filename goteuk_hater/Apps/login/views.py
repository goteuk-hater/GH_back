from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from .models import User

class UserListCreateAPI(APIView):
    def get(self, request, format=None):
        rq = User.objects.all()
        if not rq:
            return Response({'detail': 'No User Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(rq, many=True)
        return Response({'data': serializer.data})

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateDestroyAPI(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        rq = self.get_object(pk)
        if rq is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(rq)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        rq = self.get_object(pk)
        if rq is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(rq, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        rq = self.get_object(pk)
        if rq is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        rq.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

        