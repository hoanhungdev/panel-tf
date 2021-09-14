#from loguru import logger
from datetime import datetime

from moysklad.services.entities.base import get_documents, get_document_by_id
from summary_table.services.base import spreadsheet_id, \
    zakrytie_proektov_customerorder_state, search_attr_value_by_id, add, format_sum, \
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
        spreadsheet_id=spreadsheet_id, sheet='Закрытие проектов', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Закрытие проектов', start=start, 
        finish=finish
    )

def _get_link(main_doc: dict):
    return f'=ГИПЕРССЫЛКА(' \
        f'''"https://online.moysklad.ru/app/#customerorder/edit?id={main_doc['id']}";''' \
        '''"МойСклад")'''





def load_zakrytie_proektov():
    global now
    global table
    table = []
    now = datetime.now()
    customerorders = get_documents(
        doc_type='customerorder', 
        filters=[
            'applicable=true',
            f'state={zakrytie_proektov_customerorder_state}'
        ]
    )
    for id, co in enumerate(customerorders):
        co = get_document_by_id(
            doc_type='customerorder', doc_id=co['id'], 
            attributes=['expand=project, agent, organization, contract'],
        )
        table.append([])
        # проект
        project = chained_get(co, keys=['project', 'name'])
        table = _add(project)
        # дата подписания
        date1 = chained_get(co, keys=['contract', 'moment'])
        date1 = format_date(date1)
        table = _add(date1, type='date')
        # крайняя дата
        attr_id = 'a0adfc8b-e49a-11e5-7a69-8f55000cfb09'
        date2 = search_attr_value_by_id(
            attributes=chained_get(co, keys=['contract', 'attributes']),
            id=attr_id
        )
        date2 = format_date(date2)
        table = _add(date2)
        # контрагент
        agent = chained_get(co, keys=['agent', 'name'])
        table = _add(agent)
        # организация
        organization = chained_get(co, keys=['organization', 'name'])
        table = _add(organization)
        # сумма
        sum = chained_get(co, keys=['sum'])
        sum = format_sum(sum)
        table = _add(sum, type='sum')
        # оплачено
        payed = chained_get(co, keys=['payedSum'])
        payed = format_sum(payed)
        table = _add(payed, type='sum')
        # отгружено
        shipped = chained_get(co, keys=['shippedSum'])
        shipped = format_sum(shipped)
        table = _add(shipped, type='sum')
        # сделка СРМ
        attr_id = '9ae1cf7c-62be-11e8-9109-f8fc00000e42'
        crm = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        table = _add(crm)
        # папка проекта
        attr_id = 'f2418fb7-62c0-11e8-9ff4-34e8000019bb'
        project_folder = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        table = _add(project_folder)
        # группа проекта
        attr_id = 'c0fb3395-0664-11e7-7a69-8f5500041598'
        project_group = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        project_group = chained_get(project_group, keys=['name'])
        table = _add(project_group)
        # план наценка проекта
        attr_id = '4a66f181-fcb3-11e9-0a80-06b200092320'
        markup = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        table = _add(markup)
        # ФП
        attr_id = '46151e72-62be-11e8-9109-f8fc00001530'
        fp = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        fp = chained_get(fp, keys=['name'])
        table = _add(fp)
        # РП
        attr_id = '46152295-62be-11e8-9109-f8fc00001531'
        rp = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        rp = chained_get(rp, keys=['name'])
        table = _add(rp)
        # КМ
        attr_id = '7420eb28-1062-11ea-0a80-0627000b6ef3'
        km = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        km = chained_get(km, keys=['name'])
        table = _add(km)
        # СМР
        attr_id = '461526da-62be-11e8-9109-f8fc00001532'
        smr = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        smr = chained_get(smr, keys=['name'])
        table = _add(smr)
        # проект закрыт
        attr_id = '03ecc5ba-62bf-11e8-9109-f8fc00000eca'
        close = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        if close:
            close = 'Да'
        else:
            close = 'Нет'
        table = _add(close)
        # ссылка
        table = _add(_get_link(main_doc=co))
        
    h1 = [['Закрытие проектов']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей (temp@tehno-fasad) ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    h3 = [['Заказы покупателей: проведено - да, статус - Закрытие']]
    header = [[
        'Проект', 'Дата подписания', 'Крайняя дата', 'Контрагент',	'Организация',
        'Сумма', 'Оплачено', 'Отгружено', 'Сделка СРМ', 'Папка проекта', 
        'Группа проекта', 'ПланНаценкаПроекта', 'ФП', 'РП', 'КМ', 'СМР', 
        'Проект закрыт', 'Ссылка'
    ]]
    table = header + table
    
    _clear(start=7, finish=1000)
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=3, col='A', data=h3)
    _write(row=7, col='A', data=table)
    
    table = []

























