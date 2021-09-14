from moysklad.services.entities.base import get_document, get_documents
from bitrix.services.base import bx
from integrations.services.moysklad import _get_productfolders
from integrations.services.bitrix import _get_productsections, \
    _create_or_update_productsection
from integrations.services.projects.products import _get_section_id




def sync_productfolders():
    global pss
    pfs = _get_productfolders()
    pss = _get_productsections()
    pfs.sort(key=lambda pf: len(pf['pathName']))
    for productfolder in pfs:
        ps = [ps for ps in pss if ps['XML_ID'] == productfolder['id']]
        if len(ps) == 0:
            if len(productfolder['pathName']) == 0: # если папка корневая section_id=None
                _create_productsection(name=productfolder['name'], xml_id=productfolder['id'])
                pss = _get_productsections()
            else:
                _create_productsection(
                    name=productfolder['name'], xml_id=productfolder['id'], 
                    section_id=_get_section_id(productfolder)
                )
                pss = _get_productsections()
        elif len(ps) > 1:
            print(f'Больше одной папки с товарами с id: {productfolder["id"]}')
            continue
    

def process_create_event(event):
    productfolder = get_document(
        href=event.get('meta').get('href')
    )
    section_id = _get_section_id(productfolder.get('productFolder'))
    _create_or_update_productsection(
        name=productfolder['name'],
        xml_id=productfolder['id'], 
        section_id=section_id
    )

def process_delete_event(event):
    productsection = bx.callMethod(
        'crm.productsection.list', 
        filter={'XML_ID': event.get('meta').get('href')[-36:]}, 
        select=['XML_ID', 'ID']
    )
    if productsection:
        bx.callMethod('crm.productsection.delete', id=productsection[0]['ID'])
    else:
        print(f'Ошибка пи удалении по event`у: {event}')
    
def process_update_event(event):
    productfolder = get_document(
        href=event.get('meta').get('href')
    )
    productsection = bx.callMethod(
        'crm.productsection.list', 
        filter={'XML_ID': productfolder['id']}, 
        select=['XML_ID', 'ID']
    )
    if productsection:
        section_id = _get_section_id(productfolder.get('productFolder'))
        _create_or_update_productsection(
        name=productfolder['name'],
        xml_id=productfolder['id'], 
        section_id=section_id,
        id=productsection[0]['ID'])
    else:
        print(f'Ошибка пи обновлении по event`у: {event}')












