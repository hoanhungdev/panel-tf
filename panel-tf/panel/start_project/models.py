from django.db import models
from startpage.models import ProjectGroup


class DataInput(models.Model):
    project_pattern = models.CharField(max_length=128)
    project_group = models.OneToOneField(
        ProjectGroup, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f'Проект: {self.project_pattern}; Битрикс тип сделки: {self.project_group.name}'