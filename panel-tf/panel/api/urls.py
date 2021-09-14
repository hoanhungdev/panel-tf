from django.urls import path
from rest_framework.authtoken import views
from api.views import UserView

urlpatterns = [
    path('', views.obtain_auth_token),
    path('user/', UserView.as_view()),
]