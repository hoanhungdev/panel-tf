#from loguru import logger
import requests, json

from moysklad.services.base import headers, auth, base_url, MoyskladException, \
    MoyskladDocumentNotFoundException, MoyskladFewDocumentsFoundException, \
    _get, _post, _put, chunks, _process_the_response

#logger.add('/home/admin/code/panel-tf/panel/moysklad/services/entities/debug.log', format="{time} {level} {message}", level='DEBUG', rotation='1 week', compression='zip')


base_url += 'entity/'

#@logger.catch
def create_document(doc_type: str, body: dict, much_rows=True):
    """
    Принимает тип документа и данные для его создания,
    создаёт документ в мойсклад,
    возвращает созданный документ
    """
    rows_in_body = []
    try:
        items = list(body.items())
    except:
        items = []
    for item in items:
        # оставоляю по одному материалу (продукту, товару и тд) для создания документа
        if type(item[1]) == list and len(item[1]) > 1 and much_rows:
            rows_in_body.append(item)
            body[item[0]] = item[1][:1]
    
    # сущность processing нельзя создавать с отличными от processingplan`а позициями
    
    #    elif type(item[1]) == dict:
    #        # в сущности processing, product`ы указываются с вложенностью
    #        if item[1].get('rows'):
    #            rows_in_body.append(item)
    #            body[item[0]]['rows'] = item[1]['rows'][:1]
    url = f'{base_url}{doc_type}'
    response = _post(url=url, body=body)
    response = _process_the_response(response)
    for item in rows_in_body:
        # докидываю материалы (продукты, товары) в созданный документ, разбивая их по 1000 штук
        # так требует делать moysklad api 1.2
        if type(item[1]) == list and much_rows:
            _add_rows(doc_type=response['meta']['type'], doc_id=response['id'], row_type=item[0], rows=item[1][1:])
        #elif type(item[1]) == dict:
        #    if item[1].get('rows'):
        #        _add_rows(doc_type=response['meta']['type'], doc_id=response['id'], row_type=item[0], rows=item[1]['rows'][1:])
    return response

def update_documents(doc_type: str, body: dict):
    return create_document(doc_type=doc_type, body=body)
    
def update_document(doc_type: str, body: dict, doc_id: str):
    url = f'{base_url}{doc_type}/{doc_id}'
    response = _put(url=url, body=body)
    response = json.loads(response.content)
    return response

def delete_document(doc_type: str, id: str):
    """
    Принимает тип документа и идентификатор,
    удаляет документ в мойсклад
    """
    url = f'{base_url}{doc_type}/{id}'
    response = _delete(url=url)

def get_document(doc_type='', filters=[], attributes=[], href=''):
    if href:
        response = _get(href)
        return json.loads(response.content)
    else:
        documents = get_documents(doc_type=doc_type, filters=filters,
            attributes=attributes)
        if len(documents) > 1:
            raise MoyskladFewDocumentsFoundException(doc_type, filters, attributes)
        elif len(documents) == 0:
            raise MoyskladDocumentNotFoundException(doc_type, filters, attributes)
        return documents[0]

def get_documents(doc_type: str, filters=[], attributes=[]):
    """
    Принимает тип документа (например: "project", "customerorder"), filters - 
    массив строк, в которых содержатся фильтры вида: "name=1526", 
    "project.name~Гидромаш", "applicable=true" и attributes - массив строк, 
    в которых содержатся аттрибуты вида: "limit=1".
    "expand=project" не работает!
    """
    for id, filt in enumerate(filters):
        if '+' in filt:
            filters[id] = filt[:filt.index('+')]
    _attributes = '?'
    if filters:
        _attributes += 'filter=' + ';'.join(filters)
    if attributes:
        _attributes += '&'
        _attributes += '&'.join(attributes)
    url = f'{base_url}{doc_type}{_attributes}'
    rows = []
    while(True): # цикл, чтобы достать все документы по фильтру
        response = _get(url)
        response = json.loads(response.content)
        rows += response['rows']
        nextHref = response['meta'].get('nextHref')
        if nextHref:
            url = nextHref
        else:
            break
    return rows

def get_document_by_id(doc_type: str, doc_id='', id='', attributes=[]):
    """
    doc_id и id это одно и то же
    """
    if doc_id:
        id = doc_id
    if not doc_type:
        raise MoyskladException('Doc_type не может быть пустым')
    elif not id:
        raise MoyskladException('ID не может быть пустым')
    _attributes = '?'
    if attributes:
        _attributes += '&'.join(attributes)
    url = f'{base_url}{doc_type}/{id}/{_attributes}'
    response = _get(url)
    response = json.loads(response.content)
    return response

def _add_rows(doc_type: str, doc_id: str, row_type: str, rows: list):
    url = f'{base_url}{doc_type}/{doc_id}/{row_type}'
    for chunk in chunks(rows, 1000):
        response = _post(url=url, body=chunk)
        response = json.loads(response.content)

def add_materials(doc_type: str, doc_id: str, materials: list):
    _add_rows(
        doc_type=doc_type, doc_id=doc_id, 
        row_type='materials', rows=materials
    )



    
    
    
    