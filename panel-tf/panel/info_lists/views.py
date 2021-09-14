from datetime import datetime, timedelta

from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse

from django.http import HttpResponse, JsonResponse


from .tasks import load_counterparties_celery, \
                    load_projects_celery, \
                    load_expenseitems_celery, \
                    load_stores_by_webhook_task, \
                    load_product_folders_by_webhook_task, \
                    load_employees_by_webhook_task
                    

def load(request):
    type = request.GET.get('type')
    load = request.GET.get('load')
    if type == 'start':
        if load == 'contragenty':
            load_counterparties_celery.delay()
        elif load == 'proekty':
            load_projects_celery.delay()
        elif load == 'statyi_rashodov':
            load_expenseitems_celery.delay()
        elif load == 'sklady':
            load_stores_by_webhook_task.delay()
        elif load == 'gruppy_tovarov':
            load_product_folders_by_webhook_task.delay()
        elif load == 'sotrudniki':
            load_employees_by_webhook_task.delay()
    return HttpResponse('<script>window.close();</script>')





