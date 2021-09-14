from django.http import HttpResponse

from change_expenseitem.tasks import start_task

# Create your views here.
def start(request):
    start_task.delay()
    return HttpResponse('<script>window.close();</script>')