from django.urls import path

from .views import *

urlpatterns = [
    path('book_data', BookListCreateAPI.as_view()),
    path('book_category', CategoryListGetAPI.as_view()),
]