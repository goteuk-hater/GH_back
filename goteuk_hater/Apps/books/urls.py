from django.urls import path

from .views import *

urlpatterns = [
    path('book_data', BookListCreateAPI),
    path('book_category', CategoryListGetAPI),
]