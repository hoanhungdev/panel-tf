import requests, json
from decimal import Decimal

#from loguru import logger
from django.http import JsonResponse

from google_apis.services.spreadsheets.main import get_spreadsheet_rows
from moysklad.services.entities.base import create_document, get_document_by_id, \
    get_document, get_documents, delete_document
from moysklad.services.base import MoyskladException, MoyskladDocumentNotFoundException, \
    MoyskladFewDocumentsFoundException
from bitrix.services.main import get_document_by_id as get_bitrix_document_by_id
from bitrix.services.main import add_comment, update_fields
from bitrix.services.base import BitrixException, bx

from django.contrib.auth.models import User
from startpage.models import ProjectGroup
from start_project.models import DataInput

from start_project.services.base import organizations_whitelist, \
    internalorder_group_attribute_id



#logger.add('/home/admin/code/panel-tf/panel/start_project/logs/debug.log', \
#    level='DEBUG', rotation='7 days', compression='zip', retention="49 days")
    
spreadsheet_id = '1St0oJJIKf3xUhrjDv9sZG5aH6V-2Rbqidj4lR5WHqNw'

#@logger.catch
def start_project_by_webhook(deal_id: str):
    deal = _get_deal(deal_id=deal_id)
    if deal:
        return start(deal)

#@logger.catch
def start_project_by_spreadsheet_link():
    deal_id = _get_deal_id_from_spreadsheets()
    deal = _get_deal(deal_id=deal_id)
    if deal:
        return start(deal)

def _add_entity_meta(body: dict, body_key: str, entity_type: str, entity_id: str):
    entity = {
        "meta": {
            "href": f"https://online.moysklad.ru/api/remap/1.2/entity/{entity_type}/{entity_id}",
            "metadataHref": f"https://online.moysklad.ru/api/remap/1.2/entity/{entity_type}/metadata",
            "type": f"{entity_type}",
            "mediaType": "application/json"
        }
    }
    body[body_key] = entity
    return body

def _change_owner_and_group(body: dict, user_assigned_by: User):
    body = _add_entity_meta(body=body, body_key='owner', \
        entity_type='employee', entity_id=user_assigned_by.moyskladuser.id
    )
    body = _add_entity_meta(body=body, body_key='group', \
        entity_type='group', entity_id=user_assigned_by.moyskladuser.group_id
    )
    return body
    
def _get_deal_id_from_spreadsheets():
    flag = False
    rows = get_spreadsheet_rows(spreadsheet_id, sheet_name='Лист1')
    deal_id_row_num = False
    deal_id_col_num = False
    for row_id, row in enumerate(rows):
        for col_id, item in enumerate(row):
            if item == 'Создание папки проекта на ГД':
                flag = True
            if item == 'ID сделки':
                deal_id_row_num = row_id
                deal_id_col_num = col_id
                break
        if deal_id_row_num:
            break
    try:
        return int(rows[deal_id_row_num + 1][deal_id_col_num])
    except:
        raise Exception (f'Неверный ID сделки в гугл таблице: {spreadsheet_id}!')
        
def _is_deal_valid(deal):
    if deal['UF_CRM_1601677668737'].lower() == 'да': # если сделка уже прошла по алгоритму, то пропускаем её
        return False
    return True

def _get_deal(deal_id: str):
    global deal
    deal = get_bitrix_document_by_id(doc_type='crm.deal', doc_id=deal_id)
    if _is_deal_valid(deal):
        return deal
    _write_comment('Поле "Успешно созданы документы в мс" заполнено верно! ' \
        'Создание документов не производится.', stop=False)

def _write_comment(text: str, stop=True):
    add_comment(doc_type='deal', doc_id=deal['ID'], comment=text)
    if stop:
        _delete_created()
        raise Exception(text)

def _get_agent_id():
    if int(deal['COMPANY_ID']):
        try: # поиск контрагента по компании
            company = get_bitrix_document_by_id(doc_type='crm.company', 
                doc_id=deal['COMPANY_ID']
            )
            agent_id = company['UF_CRM_1450938970']
            if not agent_id:
                raise Exception('Нет agent_id!')
        except:
            _write_comment('Не найден контрагент!')
    elif int(deal['CONTACT_ID']):
        try: # поиск контрагента по контакту
            contact = get_bitrix_document_by_id(doc_type='crm.contact', 
                doc_id=deal['CONTACT_ID']
            )
            agent_id = contact['UF_CRM_1450938922']
            if not agent_id:
                raise Exception('Нет agent_id!')
        except:
            _write_comment('Не найден контрагент!')
    return agent_id

def _create_document(doc_type, body):
    doc = create_document(doc_type=doc_type, body=body)
    created.append([])
    created.append({'type': doc_type, 'id': doc['id']})
    return doc

def _delete_created():
    global created
    print('delete:' + str(created))
    created = created.reverse()
    try:
        for doc in created.reverse():
            delete_document(doc_type=doc['type'], id=doc['id'])
    except:
        add_comment(doc_type='deal', doc_id=deal['ID'], 
        comment='Неизвестная ошибка, обратитесь к администратору!'
        )


def search_service(product_name, products_require):
    try:
        moysklad_product = get_document(doc_type='service', 
            filters=[f'name~{product_name}'])
    except MoyskladFewDocumentsFoundException:
        try:
            moysklad_product = get_document(doc_type='service', 
            filters=[f'name={product_name}'])
        except MoyskladFewDocumentsFoundException:
            _write_comment('Ошибка: в мс с наименованием ' \
            f'"{product_name}" найдено ' \
            f'несколько услуг! {products_require}')
        except MoyskladDocumentNotFoundException:
            _write_comment('Ошибка: в мс с наименованием ' \
            f'"{product_name}" не найдено ' \
            f'услуг! {products_require}')
    except:
        _write_comment('Ошибка: не найден товар в мс с наименованием ' \
            f'"{product_name}"! {products_require}')
    return moysklad_product

def convert_bitrix_products_to_moysklad(bitrix_products: list):
    moysklad_products = []
    products_require = 'Все товары в сделке и предложении должны существовать в МС и иметь уникальное наименование.'
    for product in bitrix_products:
        product_name = product["ORIGINAL_PRODUCT_NAME"]
        if not product_name:
            product_name = product['PRODUCT_NAME']
        if product_name.find(';') != -1:
            product_name = product_name[:product_name.find(';')]
        try:
            moysklad_product = get_document(doc_type='product', 
                filters=[f'name~{product_name}'])
        except MoyskladDocumentNotFoundException:
            moysklad_product = search_service(product_name, products_require)
        except MoyskladFewDocumentsFoundException:
            try:
                moysklad_product = get_document(doc_type='product', 
                    filters=[f'name={product_name}'])
            except MoyskladFewDocumentsFoundException:
                _write_comment('Ошибка: в мс с наименованием ' \
                    f'"{product_name}" найдено ' \
                    f'несколько товаров! {products_require}')
            except MoyskladDocumentNotFoundException:
                moysklad_product = search_service(product_name, products_require)
        moysklad_products.append({})
        moysklad_products[len(moysklad_products) - 1]['assortment'] = {'meta': moysklad_product['meta']}
        moysklad_products[len(moysklad_products) - 1]['pathName'] = moysklad_product['pathName']
        moysklad_products[len(moysklad_products) - 1]['quantity'] = product['QUANTITY']
        moysklad_products[len(moysklad_products) - 1]['price'] = float(Decimal(product['PRICE_BRUTTO']) * 100)
        moysklad_products[len(moysklad_products) - 1]['discount'] = product['DISCOUNT_RATE']
        if product['TAX_INCLUDED'] == 'Y':
            moysklad_products[len(moysklad_products) - 1]['vat'] = int(product['TAX_RATE'])
    return moysklad_products

def get_customerorder_products(quote_sum: float):
    moysklad_products = []
    products_require = 'Все товары в сделке и предложении должны существовать в МС и иметь уникальное наименование.'
    try:
        moysklad_product = get_document(doc_type='product', 
            filters=[f'code=453767']
        )
    except MoyskladFewDocumentsFoundException:
        _write_comment('Ошибка: в мс не найден товар с кодом 453767!')
    moysklad_products.append({})
    moysklad_products[len(moysklad_products) - 1]['assortment'] = {'meta': moysklad_product['meta']}
    moysklad_products[len(moysklad_products) - 1]['pathName'] = moysklad_product['pathName']
    moysklad_products[len(moysklad_products) - 1]['quantity'] = float(quote_sum) * 100
    moysklad_products[len(moysklad_products) - 1]['price'] = float(1)
    return moysklad_products

def start(deal):
    global created
    created = []
    _write_comment('Запущено создание документов в Мой Склад. ' \
        'Ожидайте, это не займет много времени!',
        stop=False)
    deal_id = deal['ID']
    deal_title = deal['TITLE'][:50]
    if "+" in deal_title:
        _write_comment('Уберите знак "+" из названия сделки!')
    try:
        moysklad_category_id = ProjectGroup.objects.get(bitrix_id=deal['CATEGORY_ID']).moysklad_id
    except:
        _write_comment('Не найден тип проекта в мс!' \
                    'Пожалуйста обратитесь к администратору!')
    try:
        user_assigned_by = User.objects.get(bitrixuser__id=deal['ASSIGNED_BY_ID'])
    except:
        _write_comment('Не найден ответственный пользователь в базе данных!' \
                    'Пожалуйста обратитесь к администратору!')
    project_body = {
        'name': deal_title,
        'attributes': [
            { # поле проекта "Группа проекта"
                "meta":{
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/project/metadata/attributes/c0fb3395-0664-11e7-7a69-8f5500041598",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                },
                'value': {
                    "meta": {
                        "href": f"https://online.moysklad.ru/api/remap/1.2/entity/customentity/7d84a4e4-0664-11e7-7a69-971100083b11/{moysklad_category_id}",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/metadata/customEntities/7d84a4e4-0664-11e7-7a69-971100083b11",
                        "type": "customentity",
                    }
                }
            },
            { # поле проекта "ФП"
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/project/metadata/attributes/46151e72-62be-11e8-9109-f8fc00001530",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                },
                "value": {
                    "meta": {
                        "href": f"https://online.moysklad.ru/api/remap/1.2/entity/employee/{user_assigned_by.moyskladuser.id}",
                        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/employee/metadata",
                        "type": "employee",
                    }
                }
            },
            { # поле проекта "БитриксСделка"
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/project/metadata/attributes/9ae1cf7c-62be-11e8-9109-f8fc00000e42",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                },
                "value": f"https://tehnofasad.bitrix24.ru/crm/deal/show/{deal_id}/"
            },
            { # поле проекта "Папка проекта"
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/project/metadata/attributes/f2418fb7-62c0-11e8-9ff4-34e8000019bb",
                    "type": "attributemetadata",
                    "mediaType": "application/json"
                },
                "value": deal['UF_CRM_1529064940']
            },
            { # поле проекта "ПлановаяНаценкаПроекта"
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/project/metadata/attributes/4a66f181-fcb3-11e9-0a80-06b200092320",
                "type": "attributemetadata",
                "mediaType": "application/json"
            },
            "value": 1.0
            }
        ]
    }
    project_body = _change_owner_and_group(body=project_body, user_assigned_by=user_assigned_by)
    try:
        project = create_document(doc_type='project', body=project_body, much_rows=False)
    except MoyskladException:
        _write_comment('Ошибка при создании проекта!')
    store_body = {'name': deal_title}
    store_body = _change_owner_and_group(body=store_body, user_assigned_by=user_assigned_by)
    try:
        store = create_document(doc_type='store', body=store_body, much_rows=False)
    except MoyskladException:
        _write_comment('Ошибка при создании склада!')    
    try:
        company = get_bitrix_document_by_id(doc_type='crm.company', 
            doc_id=deal['UF_CRM_1601392417']
        )
        organization = get_document_by_id(doc_type='organization', 
            doc_id=company['UF_CRM_1450938970']
        )
        if not organization['id'] in organizations_whitelist:
            raise MoyskladException('organization not allowed')
    except MoyskladException:
        _write_comment('Неверная организация! Организация должна быть одной из организаций Техно Фасада!')
    except BitrixException:
        _write_comment('Не найдена организация! Проверьте поле "Организация" в сделке!')
    except MoyskladException as exc:
        print(exc) # внедрить loguru
        if exc == 'organization not allowed':
            _write_comment('В поле сделки "Организация" должна быть одна из ' \
                         'организаций Техно Фасада!')
    customerorder_body = {}
    customerorder_body = _add_entity_meta(body=customerorder_body, \
        body_key='organization', entity_type='organization', \
        entity_id=organization['id']
    )
    customerorder_body = _add_entity_meta(body=customerorder_body, \
        body_key='agent', entity_type='counterparty', \
        entity_id=_get_agent_id()
    )
    customerorder_body = _add_entity_meta(body=customerorder_body, \
        body_key='store', entity_type='store', \
        entity_id=store['id']
    )
    customerorder_body = _add_entity_meta(body=customerorder_body, \
        body_key='project', entity_type='project', \
        entity_id=project['id']
    )
    customerorder_body = _change_owner_and_group(body=customerorder_body, user_assigned_by=user_assigned_by)
    try:
        customerorder = create_document(doc_type='customerorder', body=customerorder_body, much_rows=False)
    except Exception as exc:
        error = str(exc)
        if 'organization' in error[:100]:
            _write_comment('Неверная организация!')
        elif 'counterparty' in error[:100]:
            _write_comment('Неверный контаргент! Проверьте поля Компания ' \
                         'или Контакт')
        if 'store' in error[:100]:
            _write_comment('Неверный склад!')
        if 'project' in error[:100]:
            _write_comment('Неверный проект!')
    quotes = bx.callMethod('crm.quote.list', filter={'DEAL_ID': deal_id})
    quote_require = 'Необходимо, чтобы у сделки было одно утвержденное предложение.'
    if not quotes:
        _write_comment(f'Не найдено ни одного предложения! {quote_require}')
    quotes = [quote for quote in quotes if quote['STATUS_ID'] == 'APPROVED']
    if len(quotes) == 1:
        quote = quotes[0]
    elif len(quotes) > 1:
        _write_comment(f'Найдено больше одного утвержденного предложения! {quote_require}')
    elif len(quotes) == 0:
        _write_comment(f'Не найдено утверждённое предложение! {quote_require}')
    quote_products = get_bitrix_document_by_id(
        doc_type='crm.quote.productrows', doc_id=quote['ID']
    )
    quote_products = get_customerorder_products(quote_sum=float(quote['OPPORTUNITY']))
    #quote_products = convert_bitrix_products_to_moysklad(bitrix_products=quote_products)
    try:
        customerorder_products = create_document(
            doc_type=f'customerorder/{customerorder["id"]}/positions', 
            body=quote_products
        )
    except MoyskladException:
        _write_comment('Ошибка добавления товаров в заказ покупателя!')
    deal_products = get_bitrix_document_by_id(
        doc_type='crm.deal.productrows', doc_id=deal_id
    )
    deal_products = convert_bitrix_products_to_moysklad(bitrix_products=deal_products)
    ###
    try:
        project_pattern = DataInput.objects.get(
            project_group__moysklad_id=moysklad_category_id
        ).project_pattern
    except:
        _write_comment('Не найден шаблон проекта! Обратитесь к администратору!')
    project_pattern_href = get_document(
        doc_type='project', filters=[f'name={project_pattern}']
    )['meta']['href']
    internalorders = get_documents(
        doc_type='internalorder', filters=[f'project={project_pattern_href}']
    )
    for io in internalorders:
        io_attributes = {}
        io_attributes = io.get('attributes')
        if io_attributes:
            group = [a for a in io_attributes if a['id'] == internalorder_group_attribute_id]
            if group:
                group = group[0]
                if group['value']['meta']['type'] == 'product':
                    products_body = deal_products
                elif group['value']['meta']['type'] == 'productfolder':
                    products_body = [p for p in deal_products if group['value']['name'] in p['pathName']]
            else:
                products_body = deal_products
        else:
            products_body = deal_products
        io.pop('name')
        io.pop('meta')
        io_id = io.pop('id')
        io['store'] = {}
        io['store']['meta'] = store['meta']
        io['project'] = {}
        io['project']['meta'] = project['meta']
        io['applicable'] = True
        io.pop('moment')
        purchaseOrders = []
        try:
            purchaseOrders = io.pop('purchaseOrders')
        except:
            pass
        io = _change_owner_and_group(body=io, user_assigned_by=user_assigned_by)
        new_io = create_document(
            doc_type='internalorder',
            body=io, much_rows=False
        )
        create_document(
            doc_type=f'internalorder/{new_io["id"]}/positions',
            body=products_body
        )
        for po in purchaseOrders:
            purchaseorder = get_document(doc_type='purchaseorder', href=po['meta']['href'])
            positions = get_documents(
                doc_type=f'purchaseorder/{purchaseorder["id"]}/positions'
            )
            purchaseorder.pop('moment')
            purchaseorder.pop('meta')
            purchaseorder.pop('id')
            purchaseorder.pop('name')
            purchaseorder['store'] = {}
            purchaseorder['store']['meta'] = store['meta']
            purchaseorder['project'] = {}
            purchaseorder['project']['meta'] = project['meta']
            purchaseorder['internalOrder']['meta'] = new_io['meta']
            invoicesIn = []
            try:
                invoicesIn = purchaseorder.pop('invoicesIn')
            except:
                pass
            purchaseorder = _change_owner_and_group(body=purchaseorder, user_assigned_by=user_assigned_by)
            new_purchaseorder = create_document(
                doc_type='purchaseorder',
                body=purchaseorder, much_rows=False
            )
            for p in positions:
                p.pop('meta')
                p.pop('id')
                p.pop('accountId')
            new_positions = create_document(
                doc_type=f'purchaseorder/{new_purchaseorder["id"]}/positions',
                body=positions
            )
            for ii in invoicesIn:
                invoicein = get_document(doc_type='invoicein', href=ii['meta']['href'])
                positions = get_documents(
                    doc_type=f'invoicein/{invoicein["id"]}/positions'
                )
                invoicein.pop('moment')
                invoicein.pop('meta')
                invoicein.pop('id')
                invoicein.pop('name')
                invoicein['store'] = {}
                invoicein['store']['meta'] = store['meta']
                invoicein['project'] = {}
                invoicein['project']['meta'] = project['meta']
                invoicein['purchaseOrder']['meta'] = new_purchaseorder['meta']
                supplies = []
                payments = []
                try:
                    supplies = invoicein.pop('supplies')
                except:
                    pass
                try:
                    payments = invoicein.pop('payments')
                except:
                    pass
                invoicein = _change_owner_and_group(body=invoicein, user_assigned_by=user_assigned_by)
                new_invoicein = create_document(
                    doc_type='invoicein',
                    body=invoicein, much_rows=False
                )
                for p in positions:
                    p.pop('meta')
                    p.pop('id')
                    p.pop('accountId')
                new_positions = create_document(
                    doc_type=f'invoicein/{new_invoicein["id"]}/positions',
                    body=positions
                )
                for s in supplies:
                    supply = get_document(doc_type='supply', href=s['meta']['href'])
                    positions = get_documents(
                        doc_type=f'supply/{supply["id"]}/positions'
                    )
                    supply.pop('id')
                    supply.pop('meta')
                    supply.pop('name')
                    supply.pop('moment')
                    supply['store'] = {}
                    supply['store']['meta'] = store['meta']
                    supply['project'] = {}
                    supply['project']['meta'] = project['meta']
                    supply['invoicesIn'] = [{'meta': new_invoicein['meta']}]
                    supply = _change_owner_and_group(body=supply, user_assigned_by=user_assigned_by)
                    new_supply = create_document(
                        doc_type='supply',
                        body=supply, much_rows=False
                    )
                    for p in positions:
                        p.pop('meta')
                        p.pop('id')
                        p.pop('accountId')
                    new_positions = create_document(
                        doc_type=f'supply/{new_supply["id"]}/positions',
                        body=positions
                    )
                for p in payments:
                    payment = get_document(doc_type=p['meta']['type'], href=p['meta']['href'])
                    payment.pop('moment')
                    payment.pop('id')
                    payment.pop('meta')
                    payment.pop('name')
                    payment['store'] = {}
                    payment['store']['meta'] = store['meta']
                    payment['project'] = {}
                    payment['project']['meta'] = project['meta']
                    payment['invoicesIn'] = [{'meta': new_invoicein['meta']}]
                    payment = _change_owner_and_group(body=payment, user_assigned_by=user_assigned_by)
                    new_payment = create_document(
                        doc_type=p['meta']['type'],
                        body=payment, much_rows=False
                    )
    update_fields(doc_type='crm.deal', doc_id=deal_id, \
        fields_names=['UF_CRM_1601677668737'], fields_values=['Да'])
    _write_comment('Создание документов в Мой Склад завершено успешно!', \
        stop=False)

















