#from loguru import logger
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import googleapiclient.discovery

from google_apis.services.base import CREDENTIALS_FILE
from create_project_folder.models import *
from create_project_folder.models import ProjectType, ProjectPattern, Owner
from google_apis.tasks import transfer_owner_task
from google_apis.services.spreadsheets.main import get_spreadsheet_rows
from bitrix.services.main import get_document_by_id as get_bitrix_document_by_id

#logger.add('/home/admin/code/panel-tf/panel/start_project/logs/debug.log', \
#    level='DEBUG', rotation='7 days', compression='zip', retention="49 days")
    
google_files_types = ["application/vnd.google-apps.document", "application/vnd.google-apps.site", "application/vnd.google-apps.script", "application/vnd.google-apps.presentation", "application/vnd.google-apps.drawing", "application/vnd.google-apps.document", "application/vnd.google-apps.form", "application/vnd.google-apps.spreadsheet", "application/vnd.google-apps.map"]

#@logger.catch
def create_project_folder_by_webhook(deal_id):
    deal = _get_deal(deal_id=deal_id)
    if deal:
        start(deal=deal)

#@logger.catch
def create_project_folder_by_spreadsheet_link():
    deal_id = _get_deal_id_from_spreadsheets()
    deal = _get_deal(deal_id=deal_id)
    if deal:
        start(deal=deal)

spreadsheet_id = '1St0oJJIKf3xUhrjDv9sZG5aH6V-2Rbqidj4lR5WHqNw'
def _get_deal_id_from_spreadsheets():
    flag = False
    rows = get_spreadsheet_rows(spreadsheet_id, sheet='Лист1')
    deal_id_row_num = False
    deal_id_col_num = False
    for row_id, row in enumerate(rows):
        for col_id, item in enumerate(row):
            if item == 'Создание папки проекта на ГД':
                flag = True
            if item == 'ID сделки' and flag:
                deal_id_row_num = row_id
                deal_id_col_num = col_id
                break
        if deal_id_row_num:
            break
    try:
        return int(rows[deal_id_row_num + 1][deal_id_col_num])
    except:
        raise Exception (f'Неверный ID сделки в гугл таблице: {spreadsheet_id}!')

def _get_deal(deal_id: str):
    global deal
    deal = get_bitrix_document_by_id(doc_type='crm.deal', doc_id=deal_id)
    if _is_deal_valid(deal):
        return deal
    return

def _is_deal_valid(deal):
    if deal['UF_CRM_1529064940'] != '': # если заполнена папка проекта, то пропускаем сделку
        return False
    return True

def ListOfFilesInFolder(folder_id):
    query = "'{}' in parents".format(folder_id)
    try:
        results = service_d.files().list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType, parents)").execute()
        items = results.get('files', [])
        page_token = results.get('nextPageToken')
    except Exception as exc:
        print('Нет доступа к папке с шаблоном или сервис google недоступен!')
    while True:
        if page_token != None:
            results = service_d.files().list(pageSize=1000,
                                             pageToken=page_token,
                                             fields="nextPageToken, files(id, name, mimeType)").execute()
            items.extend(results.get('files', []))
            page_token = results.get('nextPageToken')
        else:
            break
    return items

def CopyFile(item, to_folder):
    name = item['name'].replace('шаблон', project_name)
    name = name.replace('Шаблон', project_name)
    name = name.replace('ШАБЛОН', project_name)
    try:
        copy = service_d.files().copy(fileId=item['id'],
                                  body={'parents': [to_folder],
                                        'name': name}).execute()
        transfer_owner_task.delay(file_id=copy['id'], email=Owner.objects.get().email)
    except Exception as exc:
        print('Файл "{}" не удалось скопировать.'.format(name))

def Copy(items, folder_id):
    for item in items:
        if item['mimeType'] != 'application/vnd.google-apps.folder':
            CopyFile(item, folder_id)
        else:
            name = item['name'].replace('шаблон', project_name)
            name = item['name'].replace('Шаблон', project_name)
            name = item['name'].replace('ШАБЛОН', project_name)
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [folder_id]
            }
            try:
                file = service_d.files().create(body=file_metadata,
                                            fields='id').execute()
                transfer_owner_task.delay(file_id=file['id'], email=Owner.objects.get().email)
            except Exception as exc:
                print('Папку "{}" не удалось создать.'.format(name))
            copied_folder_id = file.get('id')
            items = ListOfFilesInFolder(item['id'])
            Copy(items, copied_folder_id)
import requests, json

from startpage.models import Auth
auth = (Auth.get('moysklad')[0], Auth.get('moysklad')[1])
headers = {'Content-Type': 'application/json'}



def start(deal):
    if deal['STAGE_ID'] !='NEW':
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        global service_d
        service_d = googleapiclient.discovery.build('drive', 'v3', http = httpAuth)
        global project_name
        project_name = deal['TITLE']
        category_id = deal['CATEGORY_ID']
        copy_from = ProjectPattern.objects.get(project_group__bitrix_id=category_id).google_drive_url
        smr = deal['UF_CRM_1529047870']
        copy_to = ProjectType.objects.get(bitrix_smr=smr).google_drive_url
        #copy_to = ProjectType.objects.get(name='тест').google_drive_url
        if copy_from.startswith('https://drive.google.com/drive/u'):
            copy_from_id = copy_from[43:76]
        elif copy_from.startswith('https://drive.google.com/open'):
            copy_from_id = copy_from[33:66]
        elif copy_from.startswith('https://drive.google.com/drive/folders/'):
            copy_from_id = copy_from[39:72]

        if copy_to.startswith('https://drive.google.com/drive/u'):
            copy_to_id = copy_to[43:76]
        elif copy_to.startswith('https://drive.google.com/open'):
            copy_to_id = copy_to[33:66]
        elif copy_to.startswith('https://drive.google.com/drive/folders/'):
            copy_to_id = copy_to[39:72]

        file_metadata = {
            'name': project_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [copy_to_id]
        }
        try:
            file = service_d.files().create(body=file_metadata,
                                            fields='id').execute()
            transfer_owner_task.delay(file_id=file['id'], email=Owner.objects.get().email)
        except Exception as exc:
            print(exc)
            print('Нет доступа к папке с проектами или сервис google недоступен!')
        copy_to_folder_id = file.get('id')
        prefix = 'https://drive.google.com/drive/u/0/folders/'
        url = f'https://tehnofasad.bitrix24.ru/rest/165/{Auth.get("bitrix")[0]}/crm.deal.update/?ID={deal["ID"]}&fields[UF_CRM_1529064940]={prefix + copy_to_folder_id}'
        r = requests.post(url)
        items = ListOfFilesInFolder(copy_from_id)
        Copy(items, copy_to_folder_id)
        url = f'''https://tehnofasad.bitrix24.ru/rest/165/{Auth.get("bitrix")[0]}/crm.timeline.comment.add/?fields[ENTITY_ID]={deal["ID"]}&fields[ENTITY_TYPE]=deal&fields[COMMENT]=Для сделки "{project_name.replace('#', '№')}" создана папка на ГД. \nПоле "Папка проекта на ГД" заполнено. \nСсылка: {prefix + copy_to_folder_id}'''
        r = requests.post(url)














