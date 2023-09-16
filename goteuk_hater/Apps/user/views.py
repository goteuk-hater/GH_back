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

from ..user.models import User
from ..books.models import Book, BookCategory

import asyncio
import aiohttp

LOGIN_API_ROOT = "http://classic.sejong.ac.kr/userLogin.do"
MONTHLY_CHECK_TABLE_API_ROOT = "http://classic.sejong.ac.kr/schedulePageList.do?menuInfoId=MAIN_02_04"
USER_RESERVATION_STATUS_API_ROOT = "https://classic.sejong.ac.kr/viewUserAppInfo.do?menuInfoId=MAIN_02_04"
CANCLE_API_ROOT = "https://classic.sejong.ac.kr/cencelSchedule.do?menuInfoId=MAIN_02_04"
RESERVE_API_ROOT = "https://classic.sejong.ac.kr/addAppInfo.do?menuInfoId=MAIN_02_04"
SELECT_BOOT_TERMLIST_API_ROOT = "https://classic.sejong.ac.kr/seletTermBookList.json"
RESERVE_CHECK_API_ROOT = "https://classic.sejong.ac.kr/addUserSchedule.do?menuInfoId=MAIN_02"

# "서양의역사와사상(4권)":"5 권",
# "동양의역사와사상(2권)":"4 권",
# "동·서양의 문학(3권)":"1 권",
# "과학 사상(1권)":"0 권"
class UserLoginAPI(APIView):
    # 로그인 화면에서 로그인시 필요.
    # 완료
    def post(self, request, format=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        conf = auth(id=id_, password=password_, methods=ClassicSession)
        if conf.is_auth is False:
            return Response(data='false', status=status.HTTP_401_UNAUTHORIZED)
        
        key = generate_key()
        encrypted_data = encrypt_data(password_, key)
        
        try:
            user = User.objects.get(id=id_)
            user.hash_key = key
            user.save()
        except User.DoesNotExist:
            data={"id": id_, "hash_key": key}
            User.objects.create(**data)

        info_data = conf.body
        for key in info_data['read_certification']:
            int_value, string_value = info_data['read_certification'][key].split(' ')
            info_data['read_certification'][key] = int(int_value)

        res_data = {
            "id": id_,
            "password": encrypted_data,
            "conf_data": conf.body
        }
        return Response(data=res_data, status=status.HTTP_200_OK)
            


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
        info_data = conf.body
        for key in info_data['read_certification']:
            int_value, string_value = info_data['read_certification'][key].split(' ')
            info_data['read_certification'][key] = int(int_value)
        if conf.is_auth is True:
            return Response(info_data, status=status.HTTP_200_OK) 
        return Response("False", status=status.HTTP_401_UNAUTHORIZED)

class ReservationAPI(APIView):
    # 예약 API
    def post(self, request, format=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        try:
            user = User.objects.get(id=id_)
            decrypted_data = decrypt_data(password_, user.hash_key)
            if decrypted_data is False:
                return Response("false: Wrong Password", status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response(data="false: No User Found", status=status.HTTP_404_NOT_FOUND)
        
        payload = {"userId":id_, "password":decrypted_data, "go":""}
        session = requests.Session()
        response = session.post(LOGIN_API_ROOT, data=payload)

        if response.history:
            shInfold = request.data.get("shInfold", None)
            response = session.get(RESERVE_CHECK_API_ROOT + "&shInfoId=" + shInfold)
            if response.history:
                return Response("false", status=status.HTTP_400_BAD_REQUEST)
            book_name = request.data.get("book_name", None)
            classification = request.data.get("classification", None)
            opTermId = 'TERM-00568'
            bkCode = Book.objects.get(title=book_name).id
            bkAreaCode = BookCategory.objects.get(category=classification).id

            data = {'shInfoId': shInfold, 
                    'opTermId': opTermId, 
                    'bkCode': bkCode,
                    'bkAreaCode': bkAreaCode}
            response = session.post(RESERVE_API_ROOT, data=data)

            return Response("예약 성공", status=status.HTTP_200_OK)
        else:
            return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

class ReservationCancleAPI(APIView):
    #예약 취소 
    def post(self, request, format=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        reserve_id = request.data.get("reserve_id", None)
        try:
            user = User.objects.get(id=id_)
            decrypted_data = decrypt_data(password_, user.hash_key)
            if decrypted_data is False:
                return Response("false: Wrong Password", status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response(data="false: No User Found", status=status.HTTP_404_NOT_FOUND)
        
        payload = {"userId":id_, "password":decrypted_data, "go":""}
        session = requests.Session()
        response = session.post(LOGIN_API_ROOT, data=payload)

        if response.history:
            payload = {"opAppInfoId":reserve_id}
            response = session.post(CANCLE_API_ROOT, data=payload)
            if response.history:
                return Response("취소 성공", status=status.HTTP_200_OK)
            else:
                return Response("취소 실패", status=status.HTTP_400_BAD_REQUEST)
        return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

class UserReserveStatusAPI(APIView):
    #예약 현황
    def post(self, request, format=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        try:
            user = User.objects.get(id=id_)
            decrypted_data = decrypt_data(password_, user.hash_key)
            if decrypted_data is False:
                return Response("false: Wrong Password", status=status.HTTP_401_UNAUTHORIZED)
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
                return Response(data=[], status=status.HTTP_200_OK)
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
    # 월별 빈자리 현황
    def post(self, request, fromat=None):
        id_ = request.data.get("id", None)
        password_ = request.data.get("password", None)
        try:
            user = User.objects.get(id=id_)
            decrypted_data = decrypt_data(password_, user.hash_key)
            if decrypted_data is False:
                return Response("false: Wrong Password", status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response(data="false: No User Found", status=status.HTTP_404_NOT_FOUND)
        month_data = {}
        async def login_user():
            async with aiohttp.ClientSession() as session:
                now = datetime.now()
                next_month_start = now.replace(day=1, month=now.month + 1)
                next_month = next_month_start.strftime("%Y-%m")
                start_date = now.strftime("%Y-%m")
                payload = {"userId":id_, "password":decrypted_data, "go":""}

                async with session.post(LOGIN_API_ROOT, data=payload) as response:
                    if response.history:
                        tasks = [fetch_data(session, start_date, start) for start in range(int(now.strftime("%d")) + 1, 32)]
                        tasks2 = [fetch_data(session, next_month, start) for start in range(1, int(now.strftime("%d")) + 1)]
                        await asyncio.gather(*tasks)
                        await asyncio.gather(*tasks2)
                        return Response(month_data, status=status.HTTP_200_OK)
                    else:
                        return Response("로그인 실패", status=status.HTTP_401_UNAUTHORIZED)

        async def fetch_data(session, start_date, start):
            formatted_date = start_date + "-" + str(start).zfill(2)
            payload = {"shDate": formatted_date}
            month_data[str(formatted_date)] = []
            async with session.post(MONTHLY_CHECK_TABLE_API_ROOT , data=payload) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")
                table = soup.find_all("tbody")
                tr_elements = table[0].select("tr")
                if tr_elements[0].select_one("td:nth-child(1)").text.strip() == "검색된 결과가 없습니다.":
                    return
                for tr in tr_elements:
                    if(tr.find("button")):
                        data_id = tr.find("button").get("onclick")
                        s, e = data_id.find("("), data_id.find(")")
                        data_id = data_id[s+2:e-1]
                    else:
                        data_id = ""
                    time = tr.select_one("td:nth-child(4)").text.strip()
                    available_seats = tr.select_one("td:nth-child(6)").text.strip().split()[0]
                    total_seats = tr.select_one("td:nth-child(7)").text.strip().split()[0]
                    data_in_each_time = {
                        "id": data_id,
                        "time": time,
                        "available_seats": available_seats,
                        "total_seats": total_seats,
                    }
                    month_data[str(formatted_date)].append(data_in_each_time)

        return asyncio.run(login_user())

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
