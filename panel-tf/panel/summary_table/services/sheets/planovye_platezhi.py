#from loguru import logger
from datetime import datetime

from moysklad.services.entities.base import get_documents, get_document_by_id
from summary_table.services.base import spreadsheet_id, \
    planovye_postupleniya_invoiceout_plan_state, \
    planovye_postupleniya_invoiceout_v_oplate_state, \
    planovye_platezhi_invoicein_state, search_attr_value_by_id, add, format_sum, \
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
        spreadsheet_id=spreadsheet_id, sheet='Плановые платежи', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Плановые платежи', start=start, 
        finish=finish
    )

def _get_link(doc: dict):
    return f'''=ГИПЕРССЫЛКА("https://online.moysklad.ru/app/#{doc['meta']['type']}/''' \
        f'''edit?id={doc['id']}"; "МойСклад")'''



def load_planovye_platezhi():
    global now
    global table
    table = []
    now = datetime.now()
    docs = get_documents(
        doc_type='invoiceout', 
        filters=[
            'applicable=true', 
            f'state={planovye_postupleniya_invoiceout_plan_state}', 
            f'state={planovye_postupleniya_invoiceout_v_oplate_state}'
        ]
    )
    docs += get_documents(
        doc_type='invoicein', 
        filters=['applicable=true', f'state={planovye_platezhi_invoicein_state}'], 
    )
    
    for id, doc in enumerate(docs):
        doc = get_document_by_id(
            doc_type=doc['meta']['type'], doc_id=doc['id'], 
            attributes=['expand=project, agent, organization']
        )
        table.append([])
        # проект
        project = chained_get(doc, keys=['project', 'name'])
        table = _add(project)
        # проведено
        applicable = chained_get(doc, keys=['applicable'])
        if applicable:
            table = _add('Да')
        else:
            table = _add('Нет')
        # дата счёта
        date1 = chained_get(doc, keys=['moment'])
        date1 = format_date(date1)
        table = _add(date1, type='date')
        # дата счёта
        date2 = chained_get(doc, keys=['paymentPlannedMoment'])
        date2 = format_date(date2)
        table = _add(date2, type='date')
        # контрагент
        agent = chained_get(doc, keys=['agent', 'name'])
        table = _add(agent)
        # организация
        organization = chained_get(doc, keys=['organization', 'name'])
        table = _add(organization)
        # приход и расход
        sum = chained_get(doc, keys=['sum'])
        sum = format_sum(sum)
        if chained_get(doc, keys=['meta', 'type']) == 'invoicein':
            table = _add('')
            table = _add(sum, type='sum')
        else: # doc type == invoiceout (приход)
            table = _add(sum, type='sum')
            table = _add('')
        # оплачено
        payed = chained_get(doc, keys=['payedSum'])
        payed = format_sum(payed)
        table = _add(payed, type='sum')
        # принято
        shipped = chained_get(doc, keys=['shippedSum'])
        shipped = format_sum(shipped)
        table = _add(shipped, type='sum')
        # Папка проекта
        attr_id = 'f2418fb7-62c0-11e8-9ff4-34e8000019bb'
        project_folder = search_attr_value_by_id(
            attributes=chained_get(doc, keys=['project', 'attributes']),
            id=attr_id
        )
        table = _add(project_folder)
        # Группа проекта
        attr_id = 'c0fb3395-0664-11e7-7a69-8f5500041598'
        project_group = search_attr_value_by_id(
            attributes=chained_get(doc, keys=['project', 'attributes']),
            id=attr_id
        )
        project_group = chained_get(project_group, keys=['name'])
        table = _add(project_group)
        # РП
        attr_id = '46152295-62be-11e8-9109-f8fc00001531'
        project_rp = search_attr_value_by_id(
            attributes=chained_get(doc, keys=['project', 'attributes']),
            id=attr_id
        )
        project_rp = chained_get(project_rp, keys=['name'])
        table = _add(project_rp)
        # комментарий
        desc = chained_get(doc, keys=['description'])
        table = _add(desc)
        # номер счета
        name = chained_get(doc, keys=['name'])
        table = _add(name)
        # ссылка
        table = _add(_get_link(doc=doc))
    
    h1 = [['Плановые платежи']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей (temp@tehno-fasad) ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    h3 = [['Счета поставщиков: проведено - да, статус - в плане']]
    header = [[
        'Проект', 'Проведено', 'Дата счёта', 'Плановая дата', 'Контрагент', 'Организация', 
        'Приход', 'Расход',  'Оплачено', 'Принято', 'Папка проекта', 'Группа проекта', 'РП', 'Комментарий', 'Номер счёта', 'Ссылка'
    ]]
    table = header + table
    
    _clear(start=7, finish=1000)
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=3, col='A', data=h3)
    _write(row=7, col='A', data=table)
    
    table = []



























