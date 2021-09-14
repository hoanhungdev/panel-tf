import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from integrations.models import Utm
from integrations.tasks import add_utms_task

from integrations.services.projects.products import \
    process_create_event as process_create_event_for_products, \
    process_delete_event as process_delete_event_for_products, \
    process_update_event as process_update_event_for_products
from integrations.services.projects.productfolders import \
    process_create_event as process_create_event_for_productfolders, \
    process_delete_event as process_delete_event_for_productfolders, \
    process_update_event as process_update_event_for_productfolders
from integrations.services.projects.counterparties import \
    process_create_event as process_create_event_for_counterparties, \
    process_delete_event as process_delete_event_for_counterparties, \
    process_update_event as process_update_event_for_counterparties


@csrf_exempt
def ct_hook(request):
    zd_echo = request.GET.get('zd_echo')
    if zd_echo:
        return HttpResponse(zd_echo)
    for call in json.loads(request.POST.get('result')):
        utms = Utm.objects.create(
            caller_id=call.get('caller_id'),
            source=call.get('utm_source'),
            medium=call.get('utm_medium'),
            campaign=call.get('utm_campaign'),
            term=call.get('utm_term'),
            content=call.get('utm_content'),
        )
        add_utms_task.delay(utms_id=utms.id)
    return HttpResponse(status=204)
    
@csrf_exempt
def ms_hook(request):
    events = json.loads(request.read()).get('events')
    for event in events:
        event_type = event.get('meta', {}).get('type')
        if event.get('action') == 'CREATE':
            if event_type == 'product':
                process_create_event_for_products(event)
            elif event_type == 'productfolder':
                process_create_event_for_productfolders(event)
            elif event_type == 'productfolder':
                process_create_event_for_counterparties(event)
        elif event.get('action') == 'DELETE':
            if event_type == 'product':
                process_delete_event_for_products(event)
            elif event_type == 'productfolder':
                process_delete_event_for_productfolders(event)
            elif event_type == 'productfolder':
                process_delete_event_for_counterparties(event)
        elif event.get('action') == 'UPDATE':
            if event_type == 'product':
                process_update_event_for_products(event)
            elif event_type == 'productfolder':
                process_update_event_for_productfolders(event)
            elif event_type == 'productfolder':
                process_update_event_for_counterparties(event)
        
    return HttpResponse(status=200)


