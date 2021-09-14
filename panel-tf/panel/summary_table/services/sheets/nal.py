#from loguru import logger
from datetime import datetime

from moysklad.services.entities.base import get_documents, get_document_by_id
from summary_table.services.base import spreadsheet_id, \
    nal_supply_organization, search_attr_value_by_id, add, \
    format_sum, format_date, chained_get, get_sum_by_doc_type
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range, batch_update, get_table

#logger.add(
#    '/home/admin/code/panel-tf/panel/summary_table/logs/debug.log', 
#    format="{time} {level} {message}", level='DEBUG', rotation='1 week', 
#    compression='zip', retention="49 days"
#)

def _add(item, type='str'):
    return add(to=table, item=item, type=type)

def _write(row: int, col: str, data):
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='Реестр нал', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Реестр нал', start=start, 
        finish=finish
    )

def _get_link(main_doc: dict):
    return f'''=ГИПЕРССЫЛКА("https://online.moysklad.ru/app/#supply/''' \
        f'''edit?id={main_doc['id']}"; "МойСклад")'''



def load_nal():
    SomeCells = get_table(spreadsheet_id=spreadsheet_id, sheet='Реестр нал')
    
    for Str in range(0, 1000):
        try:
            SomeCells['sheets'][0]['data'][0]['rowData'][-1]['values'][3]['formattedValue']
        except KeyError:
            SomeCells['sheets'][0]['data'][0]['rowData'].pop(-1)
        except:
            pass
    
    try:
        Strings = SomeCells['sheets'][0]['data'][0]['rowData']
    except:
        Strings = []
    try:
        Columns = SomeCells['sheets'][0]['data'][0]['rowData'][0]['values']
    except:
        Columns = []
    
    GreenArray = []
    IndexGrArr = 0
    for Str in range(0, len(Strings)):
        GreenArray.append([])
        try:
            if SomeCells['sheets'][0]['data'][0]['rowData'][Str]['values'][1]['userEnteredFormat']['backgroundColor'] == {'green': 1}:
                ##print('зеленый')
                for Col in range(0, len(Columns)):
                    try:
                        GreenArray[Str].append(SomeCells['sheets'][0]['data'][0]['rowData'][Str]['values'][Col]['formattedValue'])
                    except KeyError as exc:
                        if exc == "'formattedValue'":
                            GreenArray[Str].append('')
        except KeyError as exc:
            if exc == "'backgroundColor'":
                ##print('незеленый')
                continue
    
    global now
    global table
    table = []
    now = datetime.now()
    supplies = get_documents(
        doc_type='supply', 
        filters=['applicable=true', f'organization={nal_supply_organization}'], 
    )
    not_payed_supplies = []
    partially_payed_supplies = []
    for supp in supplies:
        if int(supp['payedSum']) == 0: # Фильтр Оплата: "Не оплачено"
            not_payed_supplies.append(supp['id'])
        elif int(supp['sum']) - int(supp['payedSum']) > 0: # Фильтр Оплата: "Частично оплачено"
            partially_payed_supplies.append(supp['id'])
    supplies = [*not_payed_supplies, *partially_payed_supplies]
    for id, supp in enumerate(supplies):
        supp = get_document_by_id(
            doc_type='supply', doc_id=supp, 
            attributes=['expand=project, agent, organization, owner, stock']
        )
        table.append([])
        # №
        table = _add('')
        # проект
        project = chained_get(supp, keys=['project', 'name'])
        table = _add(project)
        # дата приёмки
        date1 = chained_get(supp, keys=['moment'])
        date1 = format_date(date1)
        table = _add(date1, type='date')
        # №
        name = chained_get(supp, keys=['name'])
        table = _add(name)
        # контрагент
        agent = chained_get(supp, keys=['agent', 'name'])
        table = _add(agent)
        # на склад
        store = chained_get(supp, keys=['store', 'name'])
        table = _add(store)
        # сумма
        sum = chained_get(supp, keys=['sum'])
        sum = format_sum(sum)
        table = _add(sum, type='sum')
        # оплачено
        payed = chained_get(supp, keys=['payedSum'])
        payed = format_sum(payed)
        table = _add(payed, type='sum')
        # к оплате
        to_pay = sum - payed
        table = _add(to_pay, type='sum')
        # ответственный
        owner = chained_get(supp, keys=['owner', 'shortFio'])
        table = _add(owner)
        # РП
        attr_id = '46152295-62be-11e8-9109-f8fc00001531'
        project_rp = search_attr_value_by_id(
            attributes=chained_get(supp, keys=['project', 'attributes']),
            id=attr_id
        )
        project_rp = chained_get(project_rp, keys=['name'])
        table = _add(project_rp)
        # комментарий
        desc = chained_get(supp, keys=['description'])
        table = _add(desc)
        # Папка проекта
        attr_id = 'f2418fb7-62c0-11e8-9ff4-34e8000019bb'
        project_folder = search_attr_value_by_id(
            attributes=chained_get(supp, keys=['project', 'attributes']),
            id=attr_id
        )
        table = _add(project_folder)
        # ссылка
        table = _add(_get_link(main_doc=supp))
    
    h1 = [['Приёмки']]
    h2 = [
        [f'Cоздал: Сорочинский Андрей (temp@tehno-fasad) ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")} (API)']
    ]
    h3 = [['Приёмки: оплата - не оплачено/частично оплачено, проведено - да, организация - Техно Фасад']]
    header = [[
        '№', 'Проект', 'Дата приёмки', '№', 'Контрагент', 'На склад',  'Сумма', 'Оплачено', \
        'К оплате', 'Ответственный', 'РП', 'Комментарий', 'Папка проекта', 'Ссылка'
    ]]
    table = header + table
    
    _clear(start=7, finish=1000)
    _write(row=1, col='A', data=h1)
    _write(row=2, col='A', data=h2)
    _write(row=3, col='A', data=h3)
    _write(row=7, col='A', data=table)
    
    table = []

    SheetId = 1948128371
    DATA = {'requests': [{
        'repeatCell': {
            'range': {"sheetId": SheetId, 'startRowIndex': 7, 'endRowIndex': 1000},
            'cell':  {'userEnteredFormat': {"backgroundColor": {'red': 1, 'green': 1, 'blue': 1}}},
            'fields': 'userEnteredFormat.backgroundColor',}
    }]}
    batch_update(spreadsheet_id=spreadsheet_id, data=DATA)
    
    GreenArray = list(filter(None, GreenArray))
    for Greens in range(0, len(GreenArray)):
        for Str in range(0, len(table)):
            try:
                table[Str][3] = int(table[Str][3])
                GreenArray[Greens][2] = int(GreenArray[Greens][2])
            except:
                pass
            if (str(GreenArray[Greens][0]) == str(table[Str][1])) and (str(GreenArray[Greens][2]) == str(table[Str][3])) and (float(GreenArray[Greens][4].replace(',', '.')) == float(table[Str][6])):
                DATA = {'requests': [
                            {'repeatCell': {
                                'range': {"sheetId": SheetId, 'startRowIndex': Str + 6, 'endRowIndex': Str + 7},
                                'cell':  {'userEnteredFormat': {"backgroundColor": {"green": 1}}},
                                'fields': 'userEnteredFormat.backgroundColor',
                                }}
                            ]}
                batch_update(spreadsheet_id=spreadsheet_id, data=DATA)



























