import requests, json
from datetime import datetime
from startpage.models import Auth


def get_all_rows(url):
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

def sublime_filters_and_attributes(filters, attributes):
    for id, filt in enumerate(filters):
        if '+' in filt:
            filters[id] = filt[:filt.index('+')]
    _attributes = '?'
    if filters:
        _attributes += 'filter=' + ';'.join(filters)
    if attributes:
        _attributes += '&'
        _attributes += '&'.join(attributes)
    return _attributes

def chunks(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]

def _get(url: str):
    r = requests.get(url, auth=auth, headers=headers)
    if not r.ok:
        raise MoyskladException(r.text, url)
    return r

def _post(url: str, body: dict):
    r = requests.post(url, auth=auth, headers=headers, json=body)
    if not r.ok:
        raise MoyskladException(r.text, url, body)
    return r

def _delete(url: str):
    r = requests.delete(url, auth=auth, headers=headers)
    if not r.ok:
        raise MoyskladException(r.text, url)
    return r

def _put(url: str, body: dict):
    r = requests.put(url, auth=auth, headers=headers, json=body)
    if not r.ok:
        raise MoyskladException(r.text, url, body)
    return r

def _process_the_response(response):
    response = json.loads(response.content)
    if type(response) == dict:
        if response.get('moment'):
            response['moment'] = datetime.strptime(response['moment'][:-4], '%Y-%m-%d %H:%M:%S')
    return response

headers = {'Content-Type': 'application/json'}
auth = Auth.get('moysklad')

base_url = 'https://online.moysklad.ru/api/remap/1.2/'

class MoyskladException(Exception):
    pass
class MoyskladDocumentNotFoundException(MoyskladException):
    pass
class MoyskladFewDocumentsFoundException(MoyskladException):
    pass
    