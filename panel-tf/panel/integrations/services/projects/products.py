from moysklad.services.entities.base import get_document, get_documents
from bitrix.services.base import bx
from integrations.services.moysklad import _get_productfolders
from integrations.services.bitrix import _write_xml_id, \
    _get_products, _create_or_update_product, _get_productsections




def sync_products():
    global products, services, pss
    products = get_documents(doc_type='product', filters=['archived=false'])
    products += get_documents(doc_type='service', filters=['archived=false'])
    pss = _get_productsections()
    b24_products = _get_products()
    for product in products:
        product_id = product.get('id')
        p = [p for p in b24_products if p['XML_ID'] == product_id]
        if len(p) == 0:
            productfolder = get_document(
                href=product.get('productFolder', {}).get('meta', {}).get('href')
            )
            productsection_id = None
            if productfolder:
                productsection_id = [ps for ps in pss if ps["XML_ID"] == productfolder['id']][0]['ID']
            _create_or_update_product(
                name=product['name'], description=product.get('description', ''), 
                xml_id=product_id, section_id=productsection_id,
                price=product['minPrice']['value'], code=product.get('code')
            )
        elif len(p) > 1:
            print(f'Больше одного товара с id: {product_id}')

def _get_section_id(productfolder):
    pss = _get_productsections()
    if not productfolder:
        return None
    productfolder_href = productfolder.get('meta', {}).get('href')
    parent = get_document(href=productfolder_href)
    parent_ps = [ps for ps in pss if ps['XML_ID'] == parent['id']]
    if len(parent_ps) == 1:
        return parent_ps[0]['ID']
    elif len(parent_ps) == 0:
        return _create_productsection(
            name=parent['name'], xml_id=parent['id'], 
            section_id=_get_section_id(parent)
            ) # возвращается сразу ID
    elif len(ps) > 1:
        print(f'Больше одной папки с товарами с id: {productfolder["id"]}')


def process_create_event(event):
    product = get_document(
        href=event.get('meta', {}).get('href')
    )
    section_id = _get_section_id(product.get('productFolder', {}))
    _create_or_update_product(
        name=product['name'], description=product.get('description', ''), 
        xml_id=product['id'], section_id=section_id,
        price=product['minPrice']['value'], code=product.get('code')
    )

def process_delete_event(event):
    product = bx.callMethod(
        'crm.product.list', 
        filter={'XML_ID': event.get('meta', {}).get('href')[-36:]}, 
        select=['XML_ID', 'ID']
    )
    if product:
        bx.callMethod('crm.product.delete', id=product[0]['ID'])
    else:
        print(f'Ошибка пи удалении по event`у: {event}')
    
def process_update_event(event):
    product = get_document(
        href=event.get('meta', {}).get('href')
    )
    product_bx = bx.callMethod(
        'crm.product.list', 
        filter={'XML_ID': product['id']}, 
        select=['XML_ID', 'ID']
    )
    if product:
        product_id = product_bx[0]['ID']
        section_id = _get_section_id(product.get('productFolder', {}))
        _create_or_update_product(
            name=product['name'], description=product.get('description', ''), 
            xml_id=product['id'], section_id=section_id,
            price=product['minPrice']['value'], code=product.get('code'), 
            id=product_id
        )
    else:
        print(f'Ошибка пи обновлении по event`у: {event}')























