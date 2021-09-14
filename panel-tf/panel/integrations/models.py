from django.db import models

# Create your models here.
class Utm(models.Model):
    caller_id = models.TextField(null=True)
    source = models.TextField(null=True)
    medium = models.TextField(null=True)
    campaign = models.TextField(null=True)
    content = models.TextField(null=True)
    term = models.TextField(null=True)