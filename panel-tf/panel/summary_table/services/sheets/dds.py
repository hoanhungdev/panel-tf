#from loguru import logger
from datetime import datetime

from moysklad.services.entities.base import get_documents, get_document_by_id
from summary_table.services.base import spreadsheet_id, \
    dds_customerorder_state, search_attr_value_by_id, add, format_sum, \
    format_date, chained_get, get_sum_by_doc_type, first_row_with_data
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
        spreadsheet_id=spreadsheet_id, sheet='ДДС по проектам', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='ДДС по проектам', start=start, 
        finish=finish
    )

def _get_link(main_doc: dict):
    try:
        return f'''=ГИПЕРССЫЛКА("https://online.moysklad.ru/app/#cashflow''' \
            f'''?periodFilter=01.01.{now.year - 1} 00:00:00,{now.day}.{now.month}.{now.year} 23:59:00,inside_period''' \
            f'''&projectIdFilter={chained_get(main_doc, keys=['project', 'id'])},'{chained_get(main_doc, keys=['project', 'name'])},,Project"; "МойСклад")'''
    except:
        # LOGGER
        return
        


def load_dds():
    global now
    global table
    table = []
    now = datetime.now()
    customerorders = get_documents(
        doc_type='customerorder', 
        filters=['applicable=true', f'state={dds_customerorder_state}'], 
    )
    for id, co in enumerate(customerorders):
        co = get_document_by_id(
            doc_type='customerorder', doc_id=co['id'], 
            attributes=['expand=project, agent, organization, contract']
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
        table = _add(date2, type='date')
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
        # отгруженоя
        shipped = chained_get(co, keys=['shippedSum'])
        shipped = format_sum(shipped)
        table = _add(shipped, type='sum')
        # расходы безнал
        beznal_sum = get_sum_by_doc_type(doc_type='paymentout', main_doc=co)
        beznal_sum = format_sum(beznal_sum)
        table = _add(beznal_sum, type='sum')
        # расходы нал
        nal_sum = get_sum_by_doc_type(doc_type='cashout', main_doc=co)
        nal_sum = format_sum(nal_sum)
        table = _add(nal_sum, type='sum')
        # остаток денег
        row = id + first_row_with_data
        table = _add(f'=G{row}-I{row}-J{row}')
        # ссылка
        table = _add(_get_link(main_doc=co))
    
    h1 = [['ДДС по проектам']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей (temp@tehno-fasad) ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    h3 = [['Заказы покупателей: проведено - да, статус - в работе']]
    header = [[
        'Проект', 'Дата подписания', 'Крайняя дата', 'Контрагент', 'Организация', 
        'Сумма', 'Оплачено', 'Отгружено', 'Расходы безнал', 'Расходы нал', 
        'Остаток денег', 'Ссылка'
    ]]
    table = header + table
    
    _clear(start=7, finish=1000)
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=3, col='A', data=h3)
    _write(row=7, col='A', data=table)
    
    table = []

    SheetId = 2143873787
    DATA = {'requests': [{
        'repeatCell': {
            'range': {"sheetId": SheetId, 'startRowIndex': 7, 'endRowIndex': 1000},
            'cell':  {'userEnteredFormat': {"backgroundColor": {'red': 1, 'green': 1, 'blue': 1}}},
            'fields': 'userEnteredFormat.backgroundColor',}
    }]}
    batch_update(spreadsheet_id=spreadsheet_id, data=DATA)
    
    
    Colors = [{'red': 0.043137256, 'green': 0.3254902, 'blue': 0.5803922}, {'green': 1}, {'red': 1, 'green': 1}, {'red': 1, 'green': 0.6}, {'red': 1}, {'red': 0.59607846}, {'red': 0.6, 'blue': 1}, {'red': 0.2901961, 'green': 0.5254902, 'blue': 0.9098039}, {'green': 1, 'blue': 1}, {'red': 1, 'blue': 1}, {'red': 0.8666667, 'green': 0.49411765, 'blue': 0.41960785}, {'red': 0.27058825, 'green': 0.5058824, 'blue': 0.5568628}, {'red': 0.21960784, 'green': 0.4627451, 'blue': 0.11372549}, {'red': 0.21960784, 'green': 0.4627451, 'blue': 0.11372549}, {'red': 0.7490196, 'green': 0.5647059}]
    C = 0
    AmIPaint = 0
    Colorized = []
    
    for Str in range(0, len(table)):
        if AmIPaint == 1:
            AmIPaint = 0
            C = C + 1
        if not (table[Str][0] in Colorized):
            for Same in range(Str + 1, len(table)):
                if (str(table[Str][0]) == str(table[Same][0])):
                    Colorized.append(table[Str][0])
                    #print('Крашу строки: № ', Str + 1, 'и № ', Same + 1)
                    DATA = {'requests': [
                                {'repeatCell': {
                                    'range': {"sheetId": SheetId, 'startRowIndex': Str + 6, 'endRowIndex': Str + 7},
                                    'cell':  {'userEnteredFormat': {"backgroundColor": Colors[C]}},
                                    'fields': 'userEnteredFormat.backgroundColor',
                                    }},
                                {'repeatCell': {
                                    'range': {"sheetId": SheetId, 'startRowIndex': Same + 6, 'endRowIndex': Same + 7},
                                    'cell':  {'userEnteredFormat': {"backgroundColor": Colors[C]}},
                                    'fields': 'userEnteredFormat.backgroundColor',
                                    }}
                                ]}
                    AmIPaint = 1
                    Colorized.append(Str)
                    Colorized.append(Same)
                    batch_update(spreadsheet_id=spreadsheet_id, data=DATA)





























