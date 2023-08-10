from django.urls import path

from .views import *

urlpatterns = [
    path('user_list', UserListCreateAPI),
    path('<int:pk>', UserUpdateDestroyAPI)
]