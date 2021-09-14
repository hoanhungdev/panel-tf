from django.urls import path

from .views import *



urlpatterns = [
    path('get_statement', get_bank_statement),
    
]