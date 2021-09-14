from datetime import datetime, timedelta
from moysklad.services.entities.base import get_documents
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range
from info_lists.services.base import spreadsheet_id

def _write(row: int, col: str, data):
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='Контрагенты', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Контрагенты', start=start, 
        finish=finish
    )



def load_counterparties():
    counterparties = get_documents(doc_type='counterparty')
    filtered_counterparties = []
    for id, c in enumerate(counterparties):
        if (not c['name'].startswith('ООО')) and (not c['name'].startswith('ИП')) \
        and (not c['name'].startswith('ФГУП')) and (not c['name'].startswith('ТСН')) \
        and (not c['name'].startswith('ТСЖ')) and (not c['name'].startswith('ПАО')) \
        and (not c['name'].startswith('ОАО')) and (not c['name'].startswith('ЗАО')) \
        and (not c['name'].startswith('АО')):
            filtered_counterparties.append(c)

    table = []
    for id, cp in enumerate(counterparties):
        table.append([])
        try:
            table[id].append(filtered_counterparties[id]['name'])
        except:
            table[id].append('')
        table[id].append(cp['name'])
        
    date = datetime.now()
    header = [['Контрагенты'],
             ["Обновлено {}.{}.{} в {}:{}:{}".format(date.strftime("%d"), date.strftime("%m"), date.strftime("%Y"), date.strftime("%H"), date.strftime("%M"), date.strftime("%S"))],
             ['Все значения, кроме начинающихся с: ООО, ИП, ФГУП, ТСН, ТСЖ, ПАО, ОАО, ЗАО, АО'],
             [],
             [],
             ['Контрагенты', 'Все контрагенты']]
    table = [*header, *table]
    
    _clear(start='A1', finish='C1000')
    _write(row=1, col=0, data=table)
    
    
    
    
 

