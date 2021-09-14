#from loguru import logger
from datetime import datetime
from decimal import Decimal

from moysklad.services.entities.base import get_documents
from info_lists.services.base import spreadsheet_id
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range

#logger.add(
#    '/home/admin/code/panel-tf/panel/summary_table/logs/debug.log', 
#    format="{time} {level} {message}", level='DEBUG', rotation='1 week', 
#    compression='zip', retention="49 days"
#)

def _write(row: int, col: str, data):
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='Группы товаров', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Группы товаров', start=start, 
        finish=finish
    )



def load_product_folders():
    start()
def load_product_folders_by_webhook():
    start()

def start():
    now = datetime.now()
    table = []
    folders = get_documents(
        doc_type='productfolder'
    )
    for folder in folders:
        table.append([])
        table[len(table) - 1].append(folder['name'])
    table.sort()
    
    h1 = [['Группы товаров']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} в ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    header = [[
        'Название'
    ]]
    table = header + table
    
    _clear(start='A7', finish='C1000')
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=6, col='A', data=table)























