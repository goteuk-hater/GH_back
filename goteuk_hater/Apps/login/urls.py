from django.urls import path
from .views import *

urlpatterns = [
    path('auth', UserLoginAuthAPI.as_view()),
    path('reserve', UserLoginReserveAPI.as_view()),
    path('MonthlyTable', MonthResevationTableAPI.as_view()),
]