from django.urls import path

from .views import *

urlpatterns = [
    path('user_list', UserListCreateAPI.as_view()),
    path('<int:pk>', UserUpdateDestroyAPI.as_view()),
    path('login', UserLoginAPI.as_view()),
]