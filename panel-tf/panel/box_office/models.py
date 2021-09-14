from django.db import models
from django.utils import timezone

class InputData(models.Model):
    title = models.CharField('Название', max_length=255, unique=True)
    value = models.CharField('Идентификатор', max_length=255)
    
    class Meta:
        verbose_name = 'Входные данные'
        verbose_name_plural = 'Входные данные'
    
    def __str__(self):
        return f'{self.title}'

class Permission(models.Model):
    email = models.CharField(max_length=255)
    choices = (
        ('reader', 'Чтение'),
        ('commenter', 'Комментирование'),
        ('writer', 'Редактирование'),
        ('owner', 'Владелец')
    )
    role = models.CharField(max_length=16, choices=choices)
    
    class Meta:
        verbose_name = 'Право доступа'
        verbose_name_plural = 'Права доступа'
    
    def __str__(self):
        return f'{self.email}, {self.role}'
        
        