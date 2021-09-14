from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse

from .serializers import UserSerializer

class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print(request.META.get('HTTP_AUTHORIZATION'))
        token = get_object_or_404(Token, key=request.META.get('HTTP_AUTHORIZATION').replace("Token ", ""))
        serializer = UserSerializer(token.user, many=False)
        return JsonResponse(serializer.data, safe=False)
        
# дописать удаление токена, почемуто фронт е переходит на главную панели