from django.urls import path

from .views import *

urlpatterns = [
    path('get_inquiry', GetInquiryListAPI.as_view()),
    path('create_inquiry', CreateInquiryAPI.as_view()),
    path('delete_inquiry', DestroyUpdateInquiryAPI.as_view()),
    path('get_division', GetDivisionAPI.as_view()),
    path('delete_division', DestoryUpdateDivisionAPI.as_view()),
]