from django.shortcuts import render
from django.http import HttpResponse

from .tasks import proceed_single_box_office, \
                    proceed_all_box_office, \
                    load_employees_payments_task, \
                    create_report_for_all

def index(request):
    pass

def start(request):
    employees = bool(request.GET.get('employees'))
    spreadsheet = request.GET.get('spreadsheet')
    proceed_all = bool(request.GET.get('proceed_all'))
    if spreadsheet:
        proceed_single_box_office.delay(bo_link=spreadsheet)
        return HttpResponse('<script>window.close();</script>')
    elif proceed_all == True:
        proceed_all_box_office.delay()
        return HttpResponse('<script>window.close();</script>')
    elif employees:
        load_employees_payments_task.delay()
        return HttpResponse('<script>window.close();</script>')
    else:
        raise Exception
 
def create_report(request):
    create_report_for_all.delay()
 
 