from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from bonuses.tasks import *


@csrf_exempt
def webhook(request):
    sheet = request.POST.get('sheet')
    if not sheet:
        sheet = request.GET.get('sheet')
    if not sheet:
        return JsonResponse({'status': 'sheet not defined'})
    if sheet == 'all':
        load_bonus1_by_webhook_task.delay()
        load_bonus2_by_webhook_task.delay()
    if sheet == 'bonus1':
        load_bonus1_by_webhook_task.delay()
    if sheet == 'bonus2':
        load_bonus2_by_webhook_task.delay()
    if sheet == 'save':
        save_bonuses_by_webhook_task.delay()
    return HttpResponse('<script>window.close();</script>')





