from django.shortcuts import render
from django.http import HttpResponse
from processingplan.tasks import start_task
# Create your views here.

def start(request):
    start_task.delay()
    return HttpResponse('<script>window.close();</script>')
