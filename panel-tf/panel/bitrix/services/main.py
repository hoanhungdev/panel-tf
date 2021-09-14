from typing import Union
from datetime import datetime, timedelta
import requests, json

from .base import base_url, auth, BitrixException
from bitrix.services.base import bx, date_template, task_url_template



def copy_task(
        id: Union[str, int], days_to_deadline=7, 
        add_to_title='', add_to_description='',
        responsible_id=''
    ):
    source = bx.callMethod('tasks.task.get', taskId=id).get('task')
    if not source:
        raise Exception
    title = source.get('title', '') + ' ' + add_to_title
    deadline = datetime.now() + timedelta(days=days_to_deadline)
    group = source.get('group')
    if group:
        group = group.get('id')
    if not responsible_id:
        responsible_id = source['responsible']['id']
    body = {
        'TITLE': title,
        'RESPONSIBLE_ID': responsible_id,
        'DESCRIPTION': source.get('description', '') + ' ' + add_to_description,
        'CHECKLIST': source.get('checklist', []),
        'DEADLINE': deadline,
        'GROUP_ID': group
    }
    return bx.callMethod('tasks.task.add', fields=body)['task']
    

#def notify():
#    bx.callMethod(
#        'im.notify', to=responsible_id, 
#        message=f'Добавлена новая задача![br]Название: {title}' \
#        f'[br]Ссылка: {task_url_template + task["id"]}' \
#        f'[br]Ответственный: {task["responsible"]["name"]}' \
#        f'[br]Крайний срок: {_convert_datetime_to_user_friendly_string(deadline)}', 
#        type='SYSTEM')

def _convert_bitrix_date_to_datetime(date: str):
    return datetime.strptime(date, date_template)

def _convert_datetime_to_user_friendly_string(date: datetime):
    return date.strftime('%d.%m.%Y %H:%M:%S')

def get_document_by_id(doc_type: str, doc_id: str):
    url = f'{base_url}{doc_type}.get/?id={doc_id}'
    r = _post(url)
    return json.loads(r.content)['result']

def add_comment(doc_type: str, doc_id: str, comment: str):
    attributes = f"?fields[ENTITY_TYPE]={doc_type}" \
        f"&fields[ENTITY_ID]={doc_id}" \
        f"&fields[COMMENT]={comment}"
    url = f'{base_url}crm.timeline.comment.add/{attributes}'
    r = _post(url)
    return json.loads(r.content)

def update_fields(doc_type: str, doc_id: str, fields_names: list, \
        fields_values: list):
    len_fields_names = len(fields_names)
    len_fields_values = len(fields_values)
    if len_fields_names == 0:
        raise BitrixException('Пустое поле fields_names!')
    elif len_fields_values == 0:
        raise BitrixException('Пустое поле fields_values!')
    elif len_fields_names != len_fields_values:
        raise BaseException('Разная длина fields_names и fields_values!', \
            fields_names, fields_values)
    attributes = f"?id={doc_id}"
    for name_id, name in enumerate(fields_names):
        attributes += f"&fields[{name}]={fields_values[name_id]}"
    url = f'{base_url}{doc_type}.update/{attributes}'
    r = _post(url)
    return json.loads(r.content)

def _post(url):
    r = requests.post(url)
    if not r.ok:
        raise BitrixException(url, r.text)
    return r




