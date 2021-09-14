from django.db import models
from django.contrib.auth.models import User

class MoyskladUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.CharField(max_length=100, primary_key=True)
    group_id = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = 'Идентификатор МС'
        verbose_name_plural = 'Идентификаторы МС'

    def __str__(self):
        return "{}, {}".format(self.user.username, self.id)

class BitrixUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.CharField(max_length=100, primary_key=True)

    class Meta:
        verbose_name = 'Идентификатор в Битрикс'
        verbose_name_plural = 'Идентификаторы в Битрикс'

    def __str__(self):
        return "{}, {}".format(self.user.username, self.id)

class Day(models.Model):
    name_en = models.CharField(max_length=20)
    name_ru = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Наименование дня недели'
        verbose_name_plural = 'Наименования дней недели'
    
    def __str__(self):
        return '{}, id: {}'.format(self.name_ru, self.id)

class Auth(models.Model):
    login = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    service_name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Данные для входа'
        verbose_name_plural = 'Данные для входа'
    
    def get(service_name):
        auth = Auth.objects.get(service_name=service_name)
        return (auth.login, auth.password)
    
    def __str__(self):
        return '{}, id: {}'.format(self.service_name, self.id)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    initials = models.CharField(max_length=5)

    def get_name_with_initials(self):
        return "{} {}".format(self.user.last_name, self.initials)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

class InputType(models.Model):
    title = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Тип поля для ввода'
        verbose_name_plural = 'Типы поля для ввода'
    
    def __str__(self):
        return f'{self.title}'

class Input(models.Model):
    type = models.ForeignKey(InputType, default=0, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    value = models.TextField()
    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Поле для ввода'
        verbose_name_plural = 'Поля для ввода'
    
    def __str__(self):
        return f'{self.title}, id: {self.id}'

class ProjectGroup(models.Model):
    name = models.CharField('Наименование', max_length=64, unique=True)
    bitrix_id = models.CharField('Битрикс', max_length=64)
    moysklad_id = models.CharField('МойСклад', max_length=64)
    

    class Meta:
        ordering = ['-id']
        verbose_name = 'Группа проекта'
        verbose_name_plural = 'Группы проектов'

    def __str__(self):
        return self.name







