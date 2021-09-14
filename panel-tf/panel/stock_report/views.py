from django.http import HttpResponse
from .tasks import update_table_task, check_archive_task, save_table_task
# Create your views here.


def update_table(request):
    update_table_task.delay()
    return HttpResponse('<script>window.close();</script>')

def check_archive(request):
    check_archive_task.delay()
    return HttpResponse('<script>window.close();</script>')

def save_table(request):
    save_table_task.delay()
    return HttpResponse('<script>window.close();</script>')
