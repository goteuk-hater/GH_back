from django.urls import path

from .views import *

urlpatterns = [
    path('user_list', UserListCreateAPI.as_view()),
    path('<int:pk>', UserUpdateDestroyAPI.as_view()),
    path('login', UserLoginAPI.as_view()),
    path('user_info', UserLoginAuthAPI.as_view()),
    path('calender', MonthResevationTableAPI.as_view()),
    path('reserve_status', UserReserveStatusAPI.as_view()),
    path('cancle', ReservationCancleAPI.as_view()),
]