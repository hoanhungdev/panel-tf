import requests, json
from decimal import Decimal

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from start_project.tasks import start_project_by_webhook_task, \
    start_project_by_spreadsheet_link_task


@csrf_exempt
def webhook(request):
    deal_id = request.POST.get('document_id[2]').replace('DEAL_', '')
    start_project_by_webhook_task.delay(deal_id=deal_id)
    return JsonResponse({'status': 'ok'})
    


def start(request):
    start_project_by_spreadsheet_link_task.delay()
    return HttpResponse('<script>window.close();</script>')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    