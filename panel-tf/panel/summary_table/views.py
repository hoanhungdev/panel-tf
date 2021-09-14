from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from summary_table.tasks import *


@csrf_exempt
def webhook(request):
    sheet = request.POST.get('sheet')
    if not sheet:
        sheet = request.GET.get('sheet')
    if not sheet:
        return JsonResponse({'status': 'sheet not defined'})
    if sheet == 'all':
        load_dds_task.delay()
        load_debitorka_task.delay()
        load_planovye_platezhi_task.delay()
        load_planovye_postupleniya_task.delay()
        load_beznal_task.delay()
        load_nal_task.delay()
        load_reestr_proektov_task.delay()
        load_zakrytie_proektov_task.delay()
        load_vzaimoraschety_task.delay()
    if sheet == 'dds':
        load_dds_task.delay()
    if sheet == 'debitorka':
        load_debitorka_task.delay()
    if sheet == 'planovye_platezhi':
        load_planovye_platezhi_task.delay()
    if sheet == 'planovye_postupleniya':
        load_planovye_postupleniya_task.delay()
    if sheet == 'beznal':
        load_beznal_task.delay()
    if sheet == 'nal':
        load_nal_task.delay()
    if sheet == 'reestr_proektov':
        load_reestr_proektov_task.delay()
    if sheet == 'zakrytie_proektov':
        load_zakrytie_proektov_task.delay()
    if sheet == 'vzaimoraschety':
        load_vzaimoraschety_task.delay()
    if sheet == 'budgety_adm':
        load_budgety_adm_task.delay()
    if sheet == 'budget_proekta':
        load_budget_proekta_task.delay()
    return HttpResponse('<script>window.close();</script>')