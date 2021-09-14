from django.contrib import admin
from .models import Owner, ProjectPattern, ProjectType

admin.site.register(Owner)
admin.site.register(ProjectPattern)

admin.site.register(ProjectType)