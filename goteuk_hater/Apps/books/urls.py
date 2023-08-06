from django.urls import path

from .views import *

urlpatterns = [
    path('book_data', post_list),
    path('book_category', get_list_all),
]