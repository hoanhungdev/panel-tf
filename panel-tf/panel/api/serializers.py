from rest_framework import serializers
from django_celery_beat.models import PeriodicTask
from django.contrib.auth.models import User

# для инпутов (форма ввода входных данных для задачи)
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username']