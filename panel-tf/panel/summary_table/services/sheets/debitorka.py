#from loguru import logger
from datetime import datetime

from moysklad.services.entities.base import get_documents, get_document_by_id
from summary_table.services.base import spreadsheet_id, \
    search_attr_value_by_id, add, format_sum, \
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
        spreadsheet_id=spreadsheet_id, sheet='Дебиторка', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Дебиторка', start=start, 
        finish=finish
    )

def _get_link(main_doc: dict):
    return f'=ГИПЕРССЫЛКА(' \
        f'''"https://online.moysklad.ru/app/#demand/edit?id={main_doc['id']}";''' \
        '''"МойСклад")'''





def load_debitorka():
    global now
    global table
    table = []
    now = datetime.now()
    demands = get_documents(
        doc_type='demand', filters=['applicable=true'], 
    )
    not_payed_demands = []
    partially_payed_demands = []
    for dem in demands:
        if int(dem['payedSum']) == 0: # Фильтр Оплата: "Не оплачено"
            not_payed_demands.append(dem['id'])
        elif int(dem['sum']) - int(dem['payedSum']) > 0: # Фильтр Оплата: "Частично оплачено"
            partially_payed_demands.append(dem['id'])
    demands = [*not_payed_demands, *partially_payed_demands]
    
    for id, dem in enumerate(demands):
        dem = get_document_by_id(
            doc_type='demand', doc_id=dem, 
            attributes=['expand=project, agent, organization']
        )
        table.append([])
        # проект
        project = chained_get(dem, keys=['project', 'name'])
        table = _add(project)
        # дата отгрузки
        date1 = chained_get(dem, keys=['moment'])
        date1 = format_date(date1)
        table = _add(date1, type='date')
        # номер
        name = chained_get(dem, keys=['name'])
        table = _add(name)
        # организация
        organization = chained_get(dem, keys=['organization', 'name'])
        table = _add(organization)
        # контрагент
        agent = chained_get(dem, keys=['agent', 'name'])
        table = _add(agent)
        # сумма
        sum = chained_get(dem, keys=['sum'])
        sum = format_sum(sum)
        table = _add(sum, type='sum')
        # оплачено
        payed = chained_get(dem, keys=['payedSum'])
        payed = format_sum(payed)
        table = _add(payed, type='sum')
        # задолженность
        debt = sum - payed
        debt = format_sum(debt)
        table = _add(debt, type='sum')
        # ПМ проекта
        attr_id = '46152295-62be-11e8-9109-f8fc00001531'
        pm = search_attr_value_by_id(
            attributes=chained_get(dem, keys=['project', 'attributes']),
            id=attr_id
        )
        pm = chained_get(pm, keys=['name'])
        table = _add(pm)
        # Комментарий
        desc = chained_get(dem, keys=['description'])
        table = _add(desc)
        # ссылка
        table = _add(_get_link(main_doc=dem))
        
    h1 = [['Отгрузки']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей (temp@tehno-fasad) ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    h3 = [['Отгрузки: проведено - да, оплата - не оплачено и частично оплачено']]
    header = [[
        'Проект', 'Дата отгрузки', 'Номер',	'Организация', 'Контрагент', 
        'Сумма', 'Оплачено', 'Задолженность', 'ПМ проекта', 'Комментарий', 
        'Ссылка'
    ]]
    table = header + table
    
    _clear(start=7, finish=1000)
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=3, col='A', data=h3)
    _write(row=7, col='A', data=table)
    
    table = []

























