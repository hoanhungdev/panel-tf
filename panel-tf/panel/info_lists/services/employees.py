#from loguru import logger
from datetime import datetime
from decimal import Decimal

from moysklad.services.entities.base import get_documents, get_document_by_id
from info_lists.services.base import spreadsheet_id
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range
from summary_table.services.base import format_bool

#logger.add(
#    '/home/admin/code/panel-tf/panel/summary_table/logs/debug.log', 
#    format="{time} {level} {message}", level='DEBUG', rotation='1 week', 
#    compression='zip', retention="49 days"
#)

def _write(row: int, col: str, data):
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='Сотрудники', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Сотрудники', start=start, 
        finish=finish
    )



def load_employees():
    start()
def load_employees_by_webhook():
    start()

def start():
    now = datetime.now()
    table = []
    employees = get_documents(
        doc_type='employee', 
        filters=[
            'archived=false;archived=true'
        ],
        attributes=[
            'expand=group'
        ]
    )
    for emp in employees:
        emp = get_document_by_id(
            doc_type='employee', id=emp['id'], attributes=['expand=group']
        )
        table.append([])
        table[len(table) - 1].append(emp['name'])
        table[len(table) - 1].append(emp['group']['name'])
        table[len(table) - 1].append(format_bool(emp['archived']))
    table.sort()
    
    h1 = [['Сотрудники']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} в ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    h3 = [['Все сотрудники']]
    header = [[
        'ФИО', 'ОТДЕЛ', 'АРХИВНЫЙ'
    ]]
    table = header + table
    
    _clear(start='A7', finish='C1000')
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=3, col='A', data=h3)
    _write(row=6, col='A', data=table)























