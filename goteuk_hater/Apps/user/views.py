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

from ..books.models import Book

# key = generate_key()
# original_data = "암호화할 데이터"
# encrypted_data = encrypt_data(original_data, key)

LOGIN_API_ROOT = "http://classic.sejong.ac.kr/userLogin.do"
MONTHLY_CHECK_TABLE_API_ROOT = "http://classic.sejong.ac.kr/schedulePageList.do?menuInfoId=MAIN_02_04"
USER_RESERVATION_STATUS_API_ROOT = "https://classic.sejong.ac.kr/viewUserAppInfo.do?menuInfoId=MAIN_02_04"
CANCLE_API_ROOT = "https://classic.sejong.ac.kr/cencelSchedule.do?menuInfoId=MAIN_02_04"

class UserLoginAPI(APIView):
    # 로그인 화면에서 로그인시 필요.
    # 완료
    def post(self, request, format=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        print(type(id_), type(password_))
        conf = auth(id=id_, password=password_, methods=ClassicSession)
        if conf.is_auth is False:
            return Response(data='false', status=status.HTTP_401_UNAUTHORIZED)
        # if result.is_auth == False:
        #     return Response(data={"message": "Login failed."}, status=status.HTTP_401_UNAUTHORIZED)
        
        key = generate_key()
        encrypted_data = encrypt_data(password_, key)
        # return Response(data={id, password, key, encrypted_data})
        #데이터베이스에 있는지 확인
        try:
            user = User.objects.get(id=id_)
            user.hash_key = key
            user.save()
            return Response(data=encrypted_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            serializer = UserSerializer(data={"id": id_, "hash_key": key})
            if serializer.is_valid():
                serializer.save()
                return Response(encrypted_data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAuthAPI(APIView):
    # 암호화된 비밀번호를 파라미터로 입력받음. 비밀번호 변경이 되었는지를 확인.
    # 자동로그인 판별시 필요함. 
    # 완료
    def post(self, request, format=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        try:
            user = User.objects.get(id=id_)
            decrypted_data = decrypt_data(password_, user.hash_key)
        except User.DoesNotExist:
            return Response(data="false: No User Found", status=status.HTTP_404_NOT_FOUND)

        conf = auth(id=id_, password=decrypted_data, methods=ClassicSession)
        if conf.is_auth is True:
            return Response(conf.body, status=status.HTTP_200_OK) 
        return Response("False", status=status.HTTP_401_UNAUTHORIZED)
    
class UserLoginReserveAPI(APIView):
    def get(self, request, format=None):
        payload = {"userId":"", "password":"", "go":""}

        session = requests.Session()
        response = session.post(LOGIN_API_ROOT, data=payload)
     
        if response.history:
            return Response("로그인 성공", status=status.HTTP_200_OK)
        return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

class ReservationCancleAPI(APIView):
    def post(self, request, format=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        reserve_id = request.data.get("reserve_id", None)
        try:
            user = User.objects.get(id=id_)
            decrypted_data = decrypt_data(password_, user.hash_key)
        except User.DoesNotExist:
            return Response(data="false: No User Found", status=status.HTTP_404_NOT_FOUND)
        
        payload = {"userId":id_, "password":decrypted_data, "go":""}
        session = requests.Session()
        response = session.post(LOGIN_API_ROOT, data=payload)

        if response.history:
            payload = {"opAppInfoId":reserve_id}
            print(reserve_id)
            response = session.post(CANCLE_API_ROOT, data=payload)
            print(response.history)
            if response.history:
                return Response("취소 성공", status=status.HTTP_200_OK)
            else:
                return Response("취소 실패", status=status.HTTP_400_BAD_REQUEST)
        return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

class UserReserveStatusAPI(APIView):
    def post(self, request, format=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        try:
            user = User.objects.get(id=id_)
            decrypted_data = decrypt_data(password_, user.hash_key)
        except User.DoesNotExist:
            return Response(data="false: No User Found", status=status.HTTP_404_NOT_FOUND)
        
        payload = {"userId":id_, "password":decrypted_data, "go":""}
        session = requests.Session()
        response = session.post(LOGIN_API_ROOT, data=payload)

        if response.history:
            response = session.post(USER_RESERVATION_STATUS_API_ROOT)
            soup = BeautifulSoup(response.text, "html.parser")
            
            table = soup.find_all("tbody")
            tr_elements = table[0].select("tr")
            if tr_elements[0].select_one("td:nth-child(1)").text.strip() == "검색된 결과가 없습니다.":
                return Response("예약 내역이 없습니다.", status=status.HTTP_404_NOT_FOUND)
            result = []
            for data in tr_elements:
                date = data.select_one("td:nth-child(2)").text.strip()
                time = data.select_one("td:nth-child(3)").text.strip()
                location = data.select_one("td:nth-child(4)").text.strip()
                book_name = data.select_one("td:nth-child(5)").text.strip()
                reserve_id = str(data.select_one("td:nth-child(6)").select("button"))
                start_index = reserve_id.find("(")
                end_index = reserve_id.find(")")
                reserve_id = reserve_id[start_index+2:end_index-1]
                classification = Book.objects.get(title=book_name).category.category

                reserve_data = {
                    "date": date,
                    "time": time,
                    "location": location,
                    "book_name": book_name,
                    "classification": classification,
                    "reserve_id": reserve_id
                }
                result.append(reserve_data)
            return Response(data=result, status=status.HTTP_200_OK)
            
        return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

class MonthResevationTableAPI(APIView):
    # 완료
    def post(self, request, fromat=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        try:
            user = User.objects.get(id=id_)
            decrypted_data = decrypt_data(password_, user.hash_key)
        except User.DoesNotExist:
            return Response(data="false: No User Found", status=status.HTTP_404_NOT_FOUND)
        payload = {"userId":id_, "password":decrypted_data, "go":""}        
        session = requests.Session()
        response = session.post(LOGIN_API_ROOT, data=payload)

        if response.history:
            now = datetime.now()

            # 다음 달의 시작 날짜를 계산합니다.
            next_month_start = now.replace(day=1, month=now.month + 1)
            next_month = next_month_start.strftime("%Y-%m")
            
            start_date = now.strftime("%Y-%m")
            start, end = int(now.strftime("%d")) + 1, 31
            start2, end2 = int(next_month_start.day), int(now.strftime("%d"))

            month_data = {}
            # flag = False
            # data_id = 0


            while start <= end:
                print(1)
                formatted_date = start_date + "-" + str(start).zfill(2)
                month_data[str(formatted_date)] = []
                payload = {"shDate": formatted_date}
                response = session.post(MONTHLY_CHECK_TABLE_API_ROOT, data=payload)

                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find_all("tbody")

                tr_elements = table[0].select("tr")
                if tr_elements[0].select_one("td:nth-child(1)").text.strip() == "검색된 결과가 없습니다.":
                    start += 1
                    continue
                for tr in tr_elements:
                    data_id = tr.find("button").get("onclick")
                    s, e = data_id.find("("), data_id.find(")")
                    data_id = data_id[s+2:e-1]
                    time = tr.select_one("td:nth-child(4)").text.strip()
                    available_seats = tr.select_one("td:nth-child(6)").text.strip()
                    total_seats = tr.select_one("td:nth-child(7)").text.strip()
                    data_in_each_time = {
                        "id": data_id,
                        "time": time,
                        "available_seats": available_seats,
                        "total_seats": total_seats,
                    }
                    month_data[str(formatted_date)].append(data_in_each_time)
                start += 1
            flag = False
            while start2 <= end2:
                formatted_date = next_month + "-" + str(start2).zfill(2)
                month_data[str(formatted_date)] = []

                payload = {"shDate": formatted_date}
                response = session.post(MONTHLY_CHECK_TABLE_API_ROOT, data=payload)

                soup = BeautifulSoup(response.text, "html.parser")
                
                table = soup.find_all("tbody")
                tr_elements = table[0].select("tr")
                if tr_elements[0].select_one("td:nth-child(1)").text.strip() == "검색된 결과가 없습니다.":
                    start2 += 1
                    continue

                for tr in tr_elements:
                    data_id = tr.find("button").get("onclick")
                    s, e = data_id.find("("), data_id.find(")")
                    data_id = data_id[s+2:e-1]
                    time = tr.select_one("td:nth-child(4)").text.strip()
                    available_seats = tr.select_one("td:nth-child(6)").text.strip()
                    total_seats = tr.select_one("td:nth-child(7)").text.strip()
                    data_in_each_time = {
                        "id": data_id,
                        "time": time,
                        "available_seats": available_seats,
                        "total_seats": total_seats
                    }
                    month_data[str(formatted_date)].append(data_in_each_time)
                start2 += 1

            return Response(month_data, status=status.HTTP_200_OK)
        return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

class UserListCreateAPI(APIView):
    # 완료
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
    # 완료
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