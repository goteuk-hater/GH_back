from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from .models import User
from sejong_univ_auth import auth, ClassicSession
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from Apps.user.utils.encryption import *
# key = generate_key()
# original_data = "암호화할 데이터"
# encrypted_data = encrypt_data(original_data, key)

LOGIN_API_ROOT = "http://classic.sejong.ac.kr/userLogin.do"
MONTHLY_CHECK_TABLE_API_ROOT = "http://classic.sejong.ac.kr/schedulePageList.do?menuInfoId=MAIN_02_04"

class UserLoginAPI(APIView):
    # 로그인 화면에서 로그인시 필요.
    def post(self, request, format=None):
        id = request.data.get("id", None)
        password = request.data.get("password", None)
        key = generate_key()
        encrypted_data = encrypt_data(password, key)
        #데이터베이스에 있는지 확인
        rq = User.objects.filter(id=id)
        if not rq:
            #데이터베이스에 저장
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            #해당 id 값 변경
            rq = User.objects.get(id=id)
            rq.password = encrypted_data
            rq.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        
class UserLoginAuthAPI(APIView):
    # 암호화된 비밀번호를 파라미터로 입력받음. 비밀번호 변경이 되었는지를 확인.
    def post(self, request, format=None):
        conf = auth(id="", password="", methods=ClassicSession)
        if conf.is_auth is True:
            return Response(conf.body, status=status.HTTP_200_OK) 
        return Response("인증실패", status=status.HTTP_401_UNAUTHORIZED)
    # 인증 실패시 아이디와 비밀번호를 우리 데베에 암호화 해서 저장
    
class UserLoginReserveAPI(APIView):
    def get(self, request, format=None):
        payload = {"userId":"", "password":"", "go":""}

        session = requests.Session()
        response = session.post(LOGIN_API_ROOT, data=payload)
     
        if response.history:
            return Response("로그인 성공", status=status.HTTP_200_OK)
        return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

class MonthResevationTableAPI(APIView):
    def get(self, request, fromat=None):
        payload = {"userId":"", "password":"", "go":""}        
        session = requests.Session()
        response = session.post(LOGIN_API_ROOT, data=payload)

        if response.history:
            now = datetime.now()
            
            start_date = now.strftime("%Y-%m")
            start, end = int(now.strftime("%d")) + 1, int(now.strftime("31"))
            month_data = []

            while start <= end:
                formatted_date = start_date + "-" + str(start)
                payload = {"shDate": formatted_date}
                response = session.post(MONTHLY_CHECK_TABLE_API_ROOT, data=payload)

                soup = BeautifulSoup(response.text, "html.parser")
                
                table = soup.find_all("tbody")
                tr_elements = table[0].select("tr")
                day_data = []
                if tr_elements[0].select_one("td:nth-child(1)").text.strip() == "검색된 결과가 없습니다.":
                    start += 1
                    continue
                for tr in tr_elements:
                    date = tr.select_one("td:nth-child(3)").text.strip()
                    time = tr.select_one("td:nth-child(4)").text.strip()
                    available_seats = tr.select_one("td:nth-child(6)").text.strip()
                    total_seats = tr.select_one("td:nth-child(7)").text.strip()
                    data_in_each_time = {
                        "date": date,
                        "time": time,
                        "available_seats": available_seats,
                        "total_seats": total_seats
                    }
                    day_data.append(data_in_each_time)
                month_data.append(day_data)
                start += 1
            
            return Response(month_data, status=status.HTTP_200_OK)
        
        return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

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

# class UserLoginAPI(APIView):
#     def get(self, request, format=None):
#         conf = auth(id="18011489", password="hip@3326405", methods=ClassicSession)
#         if conf.is_auth is True:
#             return Response(conf, status=status.HTTP_200_OK)