from bitrix.services.base import bx
from moysklad.services.entities.base import get_document, get_documents
from integrations.services.bitrix import _create_or_update_company

from django.contrib.auth.models import User



def sync_counterparties():
    counterparties = get_documents(doc_type='counterparty', filters=['archived=false'])
    for agent in counterparties:
        company = bx.callMethod(
            'crm.company.list', 
            filter={'UF_CRM_1450938970': agent['id']}, 
            select=['UF_CRM_1450938970', 'ID']
        )
        if not company:
            _create(agent)
    
def _create_or_update(agent, id=''):
    is_my_company = 'N' if agent['meta']['type'] == 'counterparty' else 'Y'
    assigned_by_id = User.objects.get(
        moyskladuser__id=agent['owner']['meta']['href'][-36:]
    ).bitrixuser.id
    phone = agent['phone'].replace('-', '')
    phone = phone.replace('(', '').replace(')', '').replace(' ', '')
    _create_or_update_company(
        id=id,
        title=agent['name'].replace('\\', ''), 
        xml_id=agent['id'], 
        address_legal=agent['legalAddress'], 
        is_my_company=is_my_company, 
        assigned_by_id=assigned_by_id, 
        phone=phone, 
        email=agent['email']
    )

def process_create_event(event):
    agent = get_document(
        doc_type='...', # organization или counterparty 
        href=event.get('meta').get('href')
    )
    _create_or_update(agent)

def process_delete_event(event):
    agent = get_document(
        doc_type='...', # organization или counterparty 
        href=event.get('meta').get('href')
    )
    company = bx.callMethod(
        'crm.company.list', 
        filter={'UF_CRM_1450938970': agent['id']}, 
        select=['UF_CRM_1450938970', 'ID']
    )
    if company:
        bx.callMethod('crm.company.delete', id=company[0]['ID'])
    else:
        pass # ERROR

def process_update_event(event):
    agent = get_document(
        doc_type='...', # organization или counterparty 
        href=event.get('meta').get('href')
    )
    company = bx.callMethod(
        'crm.company.list', 
        filter={'UF_CRM_1450938970': agent['id']}, 
        select=['UF_CRM_1450938970', 'ID']
    )
    if company:
        _create_or_update(agent, id=company[0]['ID'])
    else:
        pass # ERROR


















