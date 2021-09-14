from moysklad.services.entities.base import get_document_by_id, \
    create_document, get_documents
from moysklad.services.base import MoyskladDocumentNotFoundException, \
    MoyskladFewDocumentsFoundException

def get_customentity_documents(id: str, filters=[], attributes=[]):
    """
    В данном случае id не является идентификатором документа.
    id - это идентификатор сущности (экземпляра customentity)
    """
    return get_documents(
        doc_type=f'customentity/{id}', filters=filters, attributes=attributes
    )

def get_customentity_document(id: str, filters=[], attributes=[]):
    documents = get_customentity_documents(
        id=id, filters=filters, attributes=attributes
    )
    if len(documents) > 1:
        raise MoyskladFewDocumentsFoundException(id, filters, attributes)
    elif len(documents) == 0:
        raise MoyskladDocumentNotFoundException(id, filters, attributes)
    return documents[0]

def get_customentity_items(id: str):
    items = []
    customentity_items = get_document_by_id(doc_type='customentity', doc_id=id)
    for item in customentity_items['rows']:
        items.append({})
        items[len(items) - 1]['name'] = item['name']
        items[len(items) - 1]['id'] = item['id']
    return items

def create_customentity_document(customentity_id: str, body: dict):
    return create_document(
        doc_type=f'customentity/{customentity_id}', body=body
    )



