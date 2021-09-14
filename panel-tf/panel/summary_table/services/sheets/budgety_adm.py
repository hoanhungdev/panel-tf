#from loguru import logger
from datetime import datetime
import calendar

from startpage.services.constants import months_full_names
from moysklad.services.entities.base import get_documents, get_document_by_id, \
    get_document
from summary_table.services.base import spreadsheet_id, \
    control_spreadsheet_id, control_sheet, \
    reestr_proektov_customerorder_state, search_attr_value_by_id, add, format_sum, \
    format_date, chained_get, get_sum_by_doc_type
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range, batch_update, get_spreadsheet_rows

#logger.add(
#    '/home/admin/code/panel-tf/panel/summary_table/logs/debug.log', 
#    format="{time} {level} {message}", level='DEBUG', rotation='1 week', 
#    compression='zip', retention="49 days"
#)

sheet = 'Бюджеты АДМ'

def _add(item, type='str'):
    return add(to=table, item=item, type=type)

def _write(row: int, col: str, data):
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet=sheet, column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet=sheet, start=start, 
        finish=finish
    )

def _get_link(doc: dict):
    return f'=ГИПЕРССЫЛКА(' \
        f'''"https://online.moysklad.ru/app/#{doc['meta']['uuidHref']}/edit?id={doc['id']}";''' \
        f'''"{doc['name']}")'''

def _write_error(text: str, raise_exception=True):
    print(write_to_sheet(spreadsheet_id=control_spreadsheet_id, sheet=control_sheet,
        column=errors_column, row_id=first_string_index+1, data=text))
    if raise_exception:
        raise

def _write_success():
    write_to_sheet(spreadsheet_id=control_spreadsheet_id, sheet=control_sheet,
        column=errors_column, row_id=first_string_index+1, data='')



def load_budgety_adm():
    rows = get_spreadsheet_rows(
        spreadsheet_id=control_spreadsheet_id, 
        sheet=control_sheet
    )
    _column_indexes(rows=rows)
    try:
        month = rows[first_string_index][month_column].lower()
        month = months_full_names.index(month) + 1
    except:
        _write_error('Укажите месяц!')
    try:
        year = int(rows[first_string_index][year_column])
    except:
        _write_error('Укажите год!')
    begin_datetime = datetime(day=1, month=month, year=year)
    last_day_in_month = calendar.monthrange(year, month)[1]
    end_datetime = datetime(day=last_day_in_month, month=month, year=year)
    global now
    global table
    table = []
    now = datetime.now()
    purchaseorders = get_documents(
        doc_type='purchaseorder', 
        filters=[
            f"moment>{begin_datetime.year}-{begin_datetime.month}-{begin_datetime.day} 00:00:00",
            f"moment<{end_datetime.year}-{end_datetime.month}-{end_datetime.day} 23:59:59"
        ]
    )
    sorted_purchaseorders = []
    for po in purchaseorders:
        attr_id = 'c0fb3395-0664-11e7-7a69-8f5500041598'
        project_href = attributes=chained_get(po, keys=['project', 'meta', 'href'])
        if project_href:
            project = get_document(doc_type='project', href=project_href)
            po['project'] = project
            attr_value = search_attr_value_by_id(
                attributes=project['attributes'], id=attr_id
            )
            if attr_value:
                if attr_value['meta']['href'] == 'https://online.moysklad.ru/api/remap/1.2/entity/customentity/7d84a4e4-0664-11e7-7a69-971100083b11/fc774bef-be63-11e9-9ff4-34e800027428' or \
                        attr_value['name'] == 'АДМ':
                    sorted_purchaseorders.append(po)
    for id, po in enumerate(sorted_purchaseorders):
        table.append([])
        # № (вн заказ)
        io = chained_get(po, keys=['internalOrder'])
        if io:
            io = get_document(doc_type='internalorder', href=io['meta']['href'])
            po['internalOrder'] = io
            table = _add(_get_link(doc=io))
        else:
            table = _add('')
        # проект
        project = chained_get(po, keys=['project', 'name'])
        table = _add(project)
        # сумма (вн заказ)
        sum = chained_get(po, keys=['internalOrder', 'sum'])
        sum = format_sum(sum)
        table = _add(sum, type='sum')
        # заказ поставщику
        table = _add(_get_link(doc=po))
        # контрагент
        agent = chained_get(po, keys=['agent'])
        if agent:
            agent = get_document(doc_type='agent', href=agent['meta']['href'])
        table = _add(agent.get('name'))
        # сумма (зак пост)
        po_sum = chained_get(po, keys=['sum'])
        po_sum = format_sum(po_sum)
        table = _add(po_sum, type='sum')
        # выставлено счетов сумма
        ii_sum = 0
        for ii in po.get('invoicesIn', []):
            ii = get_document(doc_type='invoicein', href=ii['meta']['href'])
            ii_sum += ii['sum']
        table = _add(ii_sum, type='sum')
        # оплачено (зак пост)
        po_payed_sum = chained_get(po, keys=['payedSum'])
        po_payed_sum = format_sum(po_payed_sum)
        table = _add(po_payed_sum, type='sum')
        # принято (зак пост)
        po_shipped_sum = chained_get(po, keys=['payedSum'])
        po_shipped_sum = format_sum(po_shipped_sum)
        table = _add(po_shipped_sum, type='sum')
        # описание
        description = chained_get(po, keys=['description'])
        table = _add(description)
        
        
    h1 = [['Бюджеты АДМ']]
    h2 = [
        [f'Обновлено' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} в ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")}']
    ]
    header = [[
        '№', 'Бюджет', 'Сумма бюджета', '№ заказа', 'Контрагент', 'Сумма заказа', 'Выставлено счетов', 'Оплачено', 'Принято', 'Комментарий'
    ]]
    table = header + table
    
    _clear(start=7, finish=1000)
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=7, col='A', data=table)
    _write_success()

def _column_indexes(rows: list):
    """Функция динамически определяет номера колонок"""
    for id, row in enumerate(rows):
        if row.count('Месяц') != 0:
            global first_string_index
            first_string_index = id + 1
            global month_column
            month_column = row.index('Месяц')
            global year_column
            year_column = row.index('Год')
            global errors_column
            errors_column = year_column + 2
            break




















