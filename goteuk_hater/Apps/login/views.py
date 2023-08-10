from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import User

@api_view(['GET','POST'])
def UserListCreateAPI(request):
    if request.method == 'GET':
        rq = User.objects.all()
        if not rq:
            return Response({'detail: No User Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(rq, many=True)

        return Response({'data': serializer.data})
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=404)
    
    return Response({'detail: you can only do "GET" or "POST"'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def UserUpdateDestroyAPI(request, pk):
    try:
        rq = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = UserSerializer(rq)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = UserSerializer(rq, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        rq.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        