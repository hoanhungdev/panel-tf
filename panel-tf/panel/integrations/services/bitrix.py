from integrations.models import Utm
from bitrix.services.base import bx#, bx_test

def add_utms(utms_id: int):
    utms = Utm.objects.get(id=utms_id)
    fields = {
        'UTM_SOURCE': utms.source,
        'UTM_MEDIUM': utms.medium,
        'UTM_CAMPAIGN': utms.campaign,
        'UTM_CONTENT': utms.content,
        'UTM_TERM': utms.term,
        }
    lead_list = bx.callMethod(
        'crm.lead.list',
        filter={'PHONE': utms.caller_id}
    )
    if len(lead_list) > 1:
        raise Exception(f'A lot of leads ({len(lead_list)})!')
    elif len(lead_list) < 1:
        raise Exception(f'Few leads ({len(lead_list)})!')
    response = bx.callMethod(
        'crm.lead.update', 
        id=lead_list[0]['ID'],
        fields=fields
    )
    if not response:
        raise Exception(response)
    return 'ok'
    
def _get_productsections():
    response = bx.callMethod('crm.productsection.list')
    return response
    
def _get_products():
    response = bx.callMethod('crm.product.list')
    return response

def _create_or_update_productsection(id='', name='', xml_id='', section_id=None):
    method = 'update' if id else 'add'
    response = bx.callMethod(
        f'crm.productsection.{method}', 
        id=id,
        fields={
            'NAME': name, 
            'CATALOG_ID': 24,
            'SECTION_ID': section_id,
            'XML_ID': xml_id
        }
    )
    return response

def _create_or_update_product(id='', name='', xml_id='', section_id=None, description='', price=0.00, code=None):
    method = 'update' if id else 'add'
    response = bx.callMethod(
        f'crm.product.{method}', 
        id=id,
        fields={
            'NAME': name,
            'SECTION_ID': section_id,
            'XML_ID': xml_id,
            'DESCRIPTION': description,
            'PRICE': price,
            'CODE': code
        }
    )
    return response

def _create_or_update_company(id='', title='', xml_id='', address_legal='', is_my_company=False, assigned_by_id='', phone='', email=''):
    method = 'update' if id else 'add'
    response = bx.callMethod(
        f'crm.company.{method}', 
        id=id,
        fields={
            'TITLE': title,
            'UF_CRM_1450938970': xml_id,
            'ADDRESS_LEGAL': address_legal,
            'IS_MY_COMPANY': is_my_company,
            'ASSIGNED_BY_ID': assigned_by_id,
            'PHONE': phone,
            'EMAIL': email
        }
    )
    return response

def _write_xml_id(id, xml_id):
    response = bx.callMethod(
        'crm.productsection.update', 
        id=id,
        fields={
            'XML_ID': xml_id
        }
    )
    return response






