from django.urls import path

from .views import startpage

# Create your views here.



urlpatterns = [
    path('', startpage),
]



