from django.shortcuts import render
from django.http import HttpResponse

from .tasks import get_bank_statement_celery_task
# Create your views here.

def get_bank_statement(request):
    get_bank_statement_celery_task.delay()
    return HttpResponse('<script>window.close();</script>')
