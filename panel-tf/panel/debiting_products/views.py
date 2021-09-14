from django.shortcuts import render
from django.http import HttpResponse

from .tasks import start_debiting_products, update_table_task
# Create your views here.

def start(request):
    spreadsheet = request.GET.get('spreadsheet')
    # вид ссылки: 'https://docs.google.com/spreadsheets/d/1IQjVJDighBbcFA8fD_3h6vyhxLKGLn8h-7p_mYp96Ms/edit#gid=1890343792'
    spreadsheet_id = spreadsheet[39:83]
    debit_number = request.GET.get('debit_number')
    start_debiting_products(spreadsheet_id=spreadsheet_id, debit_number=debit_number)
    return HttpResponse('<script>window.close();</script>')
    
def update_table(request):
    spreadsheet = request.GET.get('spreadsheet')
    # вид ссылки: 'https://docs.google.com/spreadsheets/d/1IQjVJDighBbcFA8fD_3h6vyhxLKGLn8h-7p_mYp96Ms/edit#gid=1890343792'
    spreadsheet_id = spreadsheet[39:83]
    update_table_task.delay(spreadsheet_id=spreadsheet_id)
    return HttpResponse('<script>window.close();</script>')

