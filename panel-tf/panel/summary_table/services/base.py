from datetime import datetime, timedelta
from decimal import Decimal

from moysklad.services.entities.base import get_documents, get_document_by_id


def search_attr_value_by_id(attributes: list, id: str):
    for attr in attributes:
        if attr['id'] == id:
            return attr['value']
            break

def add(to: list, item, type='str'):
    idx = len(to) - 1
    if not item:
        if type == 'sum':
            to[idx].append(0)
        else:
            to[idx].append('')
    elif type == 'str':
        to[idx].append(item)
    elif type == 'date':
        item = f'{item.strftime("%d")}.{item.strftime("%m")}.{item.year}'
        to[idx].append(item)
    elif type == 'sum':
        to[idx].append(float(item))
    return to

def format_sum(item):
    if not item:
        return Decimal('0.0')
    item = int(item)
    decimal = Decimal(f'{item // 100}.{str(item)[-2:]}')
    return decimal

def format_date(item: str):
    if not item:
        return
    date = datetime.strptime(item, '%Y-%m-%d %H:%M:%S.%f')
    return date

def format_bool(item):
    if item:
        return 'Да'
    return 'Нет'

def format_double(item):
    if not item:
        return 0
    return Decimal(item)

def chained_get(obj, keys: list):
    try:
        for key in keys:
            obj = obj.get(key)
    except:
        return ''
    if not obj:
        return ''
    return obj


def get_sum_by_doc_type(doc_type: str, main_doc: dict):
    now = datetime.now()
    project_href = chained_get(main_doc, keys=["project", "meta", "href"])
    if not project_href:
        return
    try:
        documents = get_documents(
            doc_type=doc_type,
            filters=[
                f'moment>={now.year - 1}-01-01', 
                f'project={project_href}']
        )
        
        sum = 0
        for doc in documents:
            sum += int(doc['sum'])
        return sum
    except Exception as exc:
        print(exc)
        # LOGGER
        return


dds_customerorder_state = 'https://online.moysklad.ru/api/remap/1.1/entity/customerorder/metadata/states/c71473c6-7c85-11e5-7a40-e897002c7347'
planovye_platezhi_invoicein_state = 'https://online.moysklad.ru/api/remap/1.1/entity/invoicein/metadata/states/f0e74bb7-3253-11e8-9107-5048000191de'
planovye_postupleniya_invoiceout_plan_state = 'https://online.moysklad.ru/api/remap/1.1/entity/invoiceout/metadata/states/44368e18-fee0-11e7-7a34-5acf000dfadd'
planovye_postupleniya_invoiceout_v_oplate_state = 'https://online.moysklad.ru/api/remap/1.1/entity/invoiceout/metadata/states/4436902e-fee0-11e7-7a34-5acf000dfade'
beznal_invoicein_na_soglasovanii_state = 'https://online.moysklad.ru/api/remap/1.1/entity/invoicein/metadata/states/c9e0298b-d67b-11e7-7a34-5acf0003833a'
nal_supply_organization = 'https://online.moysklad.ru/api/remap/1.1/entity/organization/b66837ad-d66c-11e6-7a69-9711004b5836'
reestr_proektov_customerorder_state = 'https://online.moysklad.ru/api/remap/1.1/entity/customerorder/metadata/states/c71473c6-7c85-11e5-7a40-e897002c7347'
zakrytie_proektov_customerorder_state = 'https://online.moysklad.ru/api/remap/1.1/entity/customerorder/metadata/states/f50984c0-b40b-11e9-912f-f3d400007188'
spreadsheet_id = '1N7uyxkGUuwl-V8TNwSSfRfKzktCxnatS6ZgtB3F3pzc'
first_row_with_data = 8
control_spreadsheet_id = '1St0oJJIKf3xUhrjDv9sZG5aH6V-2Rbqidj4lR5WHqNw'
control_sheet = 'Функции'











