#from loguru import logger
from datetime import datetime

from moysklad.services.entities.base import get_documents, get_document_by_id
from summary_table.services.base import spreadsheet_id, \
    planovye_postupleniya_invoiceout_plan_state, \
    planovye_postupleniya_invoiceout_v_oplate_state, search_attr_value_by_id, \
    add, format_sum, format_date, chained_get, get_sum_by_doc_type
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
        spreadsheet_id=spreadsheet_id, sheet='Плановые поступления', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Плановые поступления', start=start, 
        finish=finish
    )

def _get_link(main_doc: dict):
    return f'''=ГИПЕРССЫЛКА("https://online.moysklad.ru/app/#invoiceout/''' \
        '''edit?id={main_doc['id']}"; "МойСклад")'''




def load_planovye_postupleniya():
    global now
    global table
    table = []
    now = datetime.now()
    invoicesout = get_documents(
        doc_type='invoiceout', 
        filters=[
            'applicable=true', 
            f'state={planovye_postupleniya_invoiceout_plan_state}', 
            f'state={planovye_postupleniya_invoiceout_v_oplate_state}'
        ]
    )
    for id, io in enumerate(invoicesout):
        io = get_document_by_id(
            doc_type='invoiceout', doc_id=io['id'], 
            attributes=['expand=project, agent, organization']
        )
        table.append([])
        # проект
        project = chained_get(io, keys=['project', 'name'])
        table = _add(project)
        # дата
        date1 = chained_get(io, keys=['moment'])
        date1 = format_date(date1)
        table = _add(date1, type='date')
        # плановая дата
        date2 = chained_get(io, keys=['paymentPlannedMoment'])
        date2 = format_date(date2)
        table = _add(date2, type='date')
        # контрагент
        agent = chained_get(io, keys=['agent', 'name'])
        table = _add(agent)
        # организация
        organization = chained_get(io, keys=['organization', 'name'])
        table = _add(organization)
        # сумма
        sum = chained_get(io, keys=['sum'])
        sum = format_sum(sum)
        table = _add(sum, type='sum')
        # оплачено
        payed = chained_get(io, keys=['payedSum'])
        payed = format_sum(payed)
        table = _add(payed, type='sum')
        # Папка проекта
        attr_id = 'f2418fb7-62c0-11e8-9ff4-34e8000019bb'
        project_folder = search_attr_value_by_id(
            attributes=chained_get(io, keys=['project', 'attributes']),
            id=attr_id
        )
        table = _add(project_folder)
        # Группа проекта
        attr_id = 'c0fb3395-0664-11e7-7a69-8f5500041598'
        project_group = search_attr_value_by_id(
            attributes=chained_get(io, keys=['project', 'attributes']),
            id=attr_id
        )
        project_group = chained_get(project_group, keys=['name'])
        table = _add(project_group)
        # РП
        attr_id = '46152295-62be-11e8-9109-f8fc00001531'
        project_rp = search_attr_value_by_id(
            attributes=chained_get(io, keys=['project', 'attributes']),
            id=attr_id
        )
        project_rp = chained_get(project_rp, keys=['name'])
        table = _add(project_rp)
        # комментарий
        desc = chained_get(io, keys=['description'])
        table = _add(desc)
        # ссылка
        table = _add(_get_link(main_doc=io))
    
    h1 = [['Плановые поступления']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей (temp@tehno-fasad) ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    h3 = [['Счета покупателям: проведено - да, статус - ПЛАН и В ОПЛАТЕ']]
    header = [[
        'Проект', 'Дата', 'Плановая дата', 'Контрагент', 'Организация', 
        'Сумма', 'Оплачено', 'Папка проекта', 'Группа проекта', 'РП', 'Комментарий', 'Ссылка'
    ]]
    table = header + table
    
    _clear(start=7, finish=1000)
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=3, col='A', data=h3)
    _write(row=7, col='A', data=table)
    
    table = []



























