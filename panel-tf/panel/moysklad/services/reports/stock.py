import json
from datetime import datetime

from moysklad.services.base import base_url, _get, _post, \
    sublime_filters_and_attributes, MoyskladException


def get_report_by_doc_id(doc_id: str):
    url = f'https://online.moysklad.ru/api/remap/1.1/report/stock/byoperation?operation.id={doc_id}'
    r = _get(url)
    response = json.loads(r.content)
    return response['rows'][0]

def get_report_all(id='', href='', moment='', filters=[], attributes=[]):
    """
    id и href склада
    """
    moment_attribute = _validate_moment(moment)
    _attributes = sublime_filters_and_attributes(
        filters=filters, attributes=attributes
    )
    store = _validate_store(id=id, href=href)
    url = f'{base_url}report/stock/all{_attributes}&filter=store={store}{moment_attribute}'
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
    return {'rows': rows}

def get_report_by_store(id='', href='', moment='', filters=[], attributes=[]):
    """
    id и href склада
    """
    moment_attribute = _validate_moment(moment)
    _attributes = sublime_filters_and_attributes(
        filters=filters, attributes=attributes
    )
    store = _validate_store(id=id, href=href)
    url = f'{base_url}report/stock/bystore{_attributes}&filter=store={store}{moment_attribute}'
    r = _get(url)
    response = json.loads(r.content)
    return response
    

def _validate_store(id='', href=''):
    if id:
        return f'{base_url}entity/store/{id}'
    elif href and 'entity/store/' not in href:
        raise MoyskladException('Неверная ссылка на склад!', href)
    elif href:
        return href
    else:
        MoyskladException('Укахите id или href ссылку на склад!')

def _validate_moment(moment):
    if type(moment) != type(datetime.now()) and moment:
        raise MoyskladException('Неверный параметр "moment"!', href, moment)
    if moment:
        return f'&filter=moment={moment.strftime("%Y")}-{moment.strftime("%m")}-{moment.strftime("%d")} {moment.strftime("%H")}:{moment.strftime("%M")}:{moment.strftime("%S")}'
    else:
        return ''











