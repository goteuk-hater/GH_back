from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from sejong_univ_auth import auth, ClassicSession
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta


LOGIN_API_ROOT = "http://classic.sejong.ac.kr/userLogin.do"
MONTHLY_CHECK_TABLE_API_ROOT = "http://classic.sejong.ac.kr/schedulePageList.do?menuInfoId=MAIN_02_04"

class UserLoginAuthAPI(APIView):
    def get(self, request, format=None):
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