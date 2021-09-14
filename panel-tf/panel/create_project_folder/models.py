from django.db import models
from startpage.models import ProjectGroup

class Owner(models.Model):
    email = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Владелец копий'
        verbose_name_plural = 'Владелец копий'
    
    def __str__(self):
        return self.email

class ProjectType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    google_drive_url = models.CharField(max_length=1024)
    bitrix_smr = models.CharField('Подразделение СМР', max_length=16)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тип проекта'
        verbose_name_plural = 'Типы проектов'

    def __str__(self):
        return self.name


class ProjectPattern(models.Model):
    name = models.CharField(max_length=255, unique=True)
    google_drive_url = models.CharField(max_length=1024)
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Шаблон папки проекта'
        verbose_name_plural = 'Шаблоны папок проектов'

    def __str__(self):
        return self.name


