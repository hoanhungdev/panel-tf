import time

from panel.celery import app
from debiting_products.services.main import update_table
from debiting_products.services.debiting import start as start_debit_products


@app.task(ignore_result=True)
def update_table_task(*args, **kwargs):
    update_table(ss_id=kwargs['spreadsheet_id'])
    
@app.task(ignore_result=True)
def debit_products_task(spreadsheet_id, debit_number):
    start_debit_products(ss_id=spreadsheet_id, debit_number=debit_number)
    
def start_debiting_products(spreadsheet_id: str, debit_number: int):
    (debit_products_task.s(spreadsheet_id, debit_number=int(debit_number)) | update_table_task.s(spreadsheet_id=spreadsheet_id)).apply_async()

    


