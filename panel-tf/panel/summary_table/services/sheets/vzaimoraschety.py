#from loguru import logger
from datetime import datetime

from moysklad.services.entities.base import get_documents, get_document_by_id
from summary_table.services.base import spreadsheet_id, \
    reestr_proektov_customerorder_state, search_attr_value_by_id, add, format_sum, \
    format_date, chained_get, get_sum_by_doc_type
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range, batch_update

#logger.add(
#    '/home/admin/code/panel-tf/panel/summary_table/logs/debug.log', 
#    format="{time} {level} {message}", level='DEBUG', rotation='1 week', 
#    compression='zip', retention="49 days"
#)

def _add(item, type='str'):
    return add(to=table, item=item, type=type)

def _write(row: int, col: str, data):
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='Взаиморасчеты с сотр', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Взаиморасчеты с сотр', start=start, 
        finish=finish
    )

def _get_link(main_doc: dict):
    return f'=ГИПЕРССЫЛКА("https://online.moysklad.ru/app/#right?' \
        f'customersbalancelist?selectedAspect=WithEmployees+%7Cdetail?' \
        f'''{main_doc['id']}"; "МойСклад")'''

def get_cash_docs(emp_id: str, doc_type: str):
    docs =  get_documents(
        doc_type=doc_type, 
        filters=[f'agent=https://online.moysklad.ru/api/remap/1.1/entity/counterparty/{emp_id}'],
    )
    return docs

def get_docs_sum(docs):
    docs_sum = 0
    for doc in docs:
        docs_sum += doc.get('sum', 0)
    return format_sum(docs_sum)

def get_end_balance(emp_id: str, cashins='', cashouts=''):
    if not cashins or not cashouts:
        cashins = get_cash_docs(emp_id=emp_id, doc_type='cashin')
        cashouts = get_cash_docs(emp_id=emp_id, doc_type='cashout')
    cashins_sum = get_docs_sum(docs=cashins)
    cashouts_sum = get_docs_sum(docs=cashouts)
    end_balance = cashins_sum - cashouts_sum
    return end_balance

def get_past_date():
    if now.month == 1:
        past_date = now.replace(year=now.year-1, month=12)
    else:
        past_date = now.replace(month=now.month-1)
    return past_date

def sort_docs(docs):
    return [doc for doc in docs if format_date(doc['moment']) > past_date]

def load_vzaimoraschety():
    global now
    global table
    table = []
    now = datetime.now()
    global past_date
    past_date = get_past_date()
    
    employees = get_documents(
        doc_type='employee', 
        filters=[
            'archived=false'
        ]
    )
    for id, emp in enumerate(employees):
        emp['cashins'] = get_cash_docs(emp_id=emp['id'], doc_type='cashin')
        emp['cashouts'] = get_cash_docs(emp_id=emp['id'], doc_type='cashout')
        employees[id]['end_balance'] = get_end_balance(
            emp_id=emp['id'], cashins=emp['cashins'], cashouts=emp['cashouts']
        )
    
    employees.sort(key=lambda emp: emp['name'])
    employees = [emp for emp in employees if emp['end_balance'] != 0]
    
    for id, emp in enumerate(employees):
        sorted_cashins = sort_docs(docs=emp['cashins'])
        sorted_cashins_sum = get_docs_sum(docs=sorted_cashins)
        
        sorted_cashouts = sort_docs(docs=emp['cashouts'])
        sorted_cashouts_sum = get_docs_sum(docs=sorted_cashouts)
        
        table.append([])
        # контграгент
        agent = chained_get(emp, keys=['name'])
        table = _add(agent)
        # начальный остаток
        start_balance = chained_get(emp, keys=['end_balance'])
        start_balance -= sorted_cashins_sum - sorted_cashouts_sum
        table = _add(start_balance, type='sum')
        # приход
        table = _add(sorted_cashins_sum, type='sum')
        # расход
        table = _add(sorted_cashouts_sum, type='sum')
        # конечный остаток
        end_balance = chained_get(emp, keys=['end_balance'])
        table = _add(end_balance, type='sum')
        # касса
        attr_id = '8dc353d5-929f-11e8-9109-f8fc00104aa5'
        box_office = search_attr_value_by_id(
            attributes=chained_get(emp, keys=['attributes']),
            id=attr_id
        )
        table = _add(box_office)
        # ссылка
        table = _add(_get_link(main_doc=emp))
        
        
        
    h1 = [['Взаиморасчеты с сотрудниками']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей (temp@tehno-fasad) ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    
    header = [[
        'Контрагент', 'Начальный остаток', 'Приход', 'Расход', \
        'Конечный остаток', 'Касса', 'Ссылка'
    ]]
    table = header + table
    
    _clear(start=7, finish=1000)
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=7, col='A', data=table)
    
    table = []

























