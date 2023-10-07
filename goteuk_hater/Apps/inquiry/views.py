from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .serializers import InquirySerializer, DivisionSerializer
from .models import Inquiry, Division

class GetInquiryListAPI(APIView):
    def get(self, request, format=None):
        inquiry = Inquiry.objects.all()
        serializer = InquirySerializer(inquiry, many=True)

        return Response({'data': serializer.data})
    
class CreateInquiryAPI(APIView):
    def post(self, request, format=None):
        serializer = InquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class DestroyUpdateInquiryAPI(APIView):
    def delete(self, request, format=None):
        id_ = request.data.get('id')
        if not id_:
            inquiry = Inquiry.objects.all().delete()
        inquiry = Inquiry.objects.get(id=id_).delete()

        if inquiry:
            return Response({'detail': 'Inquiry deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Inquiry to delete not found'}, status=status.HTTP_404_NOT_FOUND)

class GetDivisionAPI(APIView):
    def get(self, request, format=None):
        division = Division.objects.all()
        serializer = DivisionSerializer(division, many=True)

        return Response({'data': serializer.data})
    
class DestoryUpdateDivisionAPI(APIView):
    def delete(self, request, format=None):
        id_ = request.data.get('id')
        if not id_:
            division = Division.objects.all().delete()
        division = Division.objects.get(id=id_).delete()

        if division:
            return Response({'detail': 'Division deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Division to delete not found'}, status=status.HTTP_404_NOT_FOUND)  