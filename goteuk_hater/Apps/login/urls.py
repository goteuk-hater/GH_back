from django.urls import path

from .views import UserListCreateAPIView, UserRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', UserListCreateAPIView.as_view()),
    path('user/<user_id>', UserRetrieveUpdateDestroyAPIView.as_view())
]