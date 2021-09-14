from datetime import datetime, timedelta
from moysklad.services.entities.base import get_documents
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range
from info_lists.services.base import spreadsheet_id

def _write(row: int, col: str, data):
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='Статьи расходов', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Статьи расходов', start=start, 
        finish=finish
    )



def load_expenseitems():
    expenseitems = get_documents(doc_type='expenseitem')

    table = []
    for id, ei in enumerate(expenseitems):
        table.append([])
        table[id].append(ei['name'])
    
    table.pop(table.index(['Списания']))
    table.sort()
    
    date = datetime.now()
    header = [['Статьи расходов'],
             ["Обновлено {}.{}.{} в {}:{}:{}".format(date.strftime("%d"), date.strftime("%m"), date.strftime("%Y"), date.strftime("%H"), date.strftime("%M"), date.strftime("%S"))],
             [],
             [],
             [],
             ['Статьи расходов']]
    table = [*header, *table]
    
    _clear(start='A1', finish='C1000')
    _write(row=1, col=0, data=table)
    
    
    
    
 

















