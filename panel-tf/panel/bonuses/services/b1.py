#from loguru import logger
import calendar
from datetime import datetime
from decimal import Decimal

from moysklad.services.entities.base import get_documents, get_document_by_id
from bonuses.services.base import spreadsheet_id, b1_sheet_id, summary_sheet_id, \
    get_dates_from_spreadsheets
from summary_table.services.base import reestr_proektov_customerorder_state, search_attr_value_by_id, add, format_sum, \
    format_date, format_bool, format_double, chained_get, get_sum_by_doc_type
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
        spreadsheet_id=spreadsheet_id, sheet='Бонус 1', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Бонус 1', start=start, 
        finish=finish
    )

def _get_link(doc: dict, type: str, text: str):
    if not doc or not text:
        return ''
    return f'=ГИПЕРССЫЛКА(' \
        f'''"https://online.moysklad.ru/app/#{type}/edit?id={doc['id']}";''' \
        f'''"{text}")'''


def load_bonus1():
    start()
def load_bonus1_by_webhook():
    dates = get_dates_from_spreadsheets()
    start(dates)

def start(dates={}):
    global now
    global table
    table = []
    now = datetime.now()
    if not dates:
        if now.month >= 5:
            date_from = datetime(day=1, month=4, year=now.year)
        elif now.month < 5:
            date_from = datetime(day=1, month=4, year=now.year-1)
        date_to = now
        print(date_to)
        monthrange = calendar.monthrange(now.year, now.month-1)
        date_to = date_to.replace(month=date_to.month-1, day=monthrange[1])
        print(date_to)
    else:
        date_from = dates['date_from']
        date_to = dates['date_to']
    customerorders = get_documents(
        doc_type='customerorder', 
        filters=[
            'applicable=true',
            f'moment>{date_from.year}-{date_from.month}-{date_from.day} 00:00:00',
            f'moment<{date_to.year}-{date_to.month}-{date_to.day} 23:59:59',
        ]
    )
    
    
    
    for id, co in enumerate(customerorders):
        co = get_document_by_id(
            doc_type='customerorder', doc_id=co['id'], 
            attributes=['expand=project, agent, organization, contract.state'],
        )
        table.append([])
        # дата заказа покупателя
        date1 = chained_get(co, keys=['moment'])
        date1 = format_date(date1)
        table = _add(date1, type='date')
        # № заказа покупателя
        table = _add(_get_link(doc=co, type='customerorder', text=chained_get(co, keys=['name'])))
        # контрагент
        agent = chained_get(co, keys=['agent', 'name'])
        table = _add(agent)
        # организация
        organization = chained_get(co, keys=['organization', 'name'])
        table = _add(organization)
        # проект
        project = chained_get(co, keys=['project'])
        project = _get_link(doc=project, type='project', text=chained_get(project, keys=['name']))
        table = _add(project)
        # сумма
        sum = chained_get(co, keys=['sum'])
        sum = format_sum(sum)
        table = _add(sum, type='sum')
        # оплачено
        payed = chained_get(co, keys=['payedSum'])
        payed = format_sum(payed)
        table = _add(payed, type='sum')
        # статус договора
        contract_state = chained_get(co, keys=['contract', 'state', 'name'])
        table = _add(contract_state)
        # сумма договора
        contract_sum = chained_get(co, keys=['contract', 'sum'])
        contract_sum = format_sum(contract_sum)
        table = _add(contract_sum, type='sum')
        # сумма аванса
        attr_id = 'fb58953e-150c-11ea-0a80-064d00247cf8'
        prepaid = search_attr_value_by_id(
            attributes=chained_get(co, keys=['contract', 'attributes']),
            id=attr_id
        )
        table = _add(prepaid)
        # карточка проекта утверждена
        attr_id = '8cd7960f-80a2-11ea-0a80-05d400106a4b'
        approved = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        approved = format_bool(approved)
        table = _add(approved)
        # группа проекта
        attr_id = 'c0fb3395-0664-11e7-7a69-8f5500041598'
        project_group = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        project_group = chained_get(project_group, keys=['name'])
        table = _add(project_group)
        # план наценка
        attr_id = '4a66f181-fcb3-11e9-0a80-06b200092320'
        markup = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        markup = format_double(markup)
        table = _add(markup, type='sum')
        # бонус 1 начислен
        attr_id = 'f2d87a9c-d0b4-11e9-0a80-01810000490b'
        bonus1 = search_attr_value_by_id(
            attributes=chained_get(co, keys=['project', 'attributes']),
            id=attr_id
        )
        bonus1 = format_bool(bonus1)
        table = _add(bonus1)
        # пустые поля
        table = _add('')
        table = _add('')
        table = _add('')
        table = _add('')
        table = _add('')
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
        # пустое поле
        table = _add('')
    
    h1 = f'Успешно обновлено! ({now.strftime("%d")}.{now.strftime("%m")}' \
        f'.{now.year} {now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")})'
    h2 = [[
        'Проведённые заказы покупателей за период с ' \
        f'{date_from.strftime("%d")}.{date_from.strftime("%m")}.{date_from.year}' \
        f' по {date_to.strftime("%d")}.{date_to.strftime("%m")}.{date_to.year}'
    ]]
    
    #header = [[
    #    'Дата Заказа покупателя','№ Заказа покупателя',	'Контрагент', 'Организация', 'Проект', 'Сумма Заказа покупателя', 'Оплачено',
    #    'Статус договора', 'Сумма договора', 'Сумма аванса', 'Карточка проекта утверждена',
    #    'Группа проекта', 'План.наценка', 'Бонус 1 начислен', 'КВ', 'ПП', 
    #    'ПЗ', 'ПР', 'СП', 'ФП', 'КМ', 'РП', 'СМР'
    #]]
    #table = header + table
    
    _clear(start='A8', finish='X1000')
    _write(row=3, col='A', data=h1)
    _write(row=4, col='A', data=h2)
    _write(row=8, col='A', data=table)
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='Сводная таблица бонусов', column='F', 
        row_id=3, 
        data=h1
    )

    body = {'requests': [
        {
            "setBasicFilter": {
                "filter": {
                    'range' : {
                        "sheetId": b1_sheet_id,
                        "startRowIndex": 6,
                        "endRowIndex": 394,
                        "startColumnIndex": 0,
                        "endColumnIndex": 27
                    },
                    'criteria' : {
                        "13": {
                            "hiddenValues": [
                                "",
                                "Да"
                            ]
                        }
                    }
                }
            }
        },
        {
            "setBasicFilter": {
                "filter": {
                    'range' : {
                        "sheetId": summary_sheet_id,
                        "startRowIndex": 6,
                        "endRowIndex": 394,
                        "startColumnIndex": 0,
                        "endColumnIndex": 27
                    },
                    'criteria' : {
                        "0": {
                            "hiddenValues": [
                                "НЕТ"
                            ]
                        }
                    }
                }
            }
        }
    ]}
    batch_update(spreadsheet_id=spreadsheet_id, data=body)























