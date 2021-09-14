import apiclient.discovery
from google_apis.services.base import httpAuth, developerKey

def _get_drive_service():
    return apiclient.discovery.build('drive', 'v3', http = httpAuth)

def give_permission(item_id: str, email: str, role: str):
    service = _get_drive_service()
    transfer_ownership = False
    if role == 'owner':
        transfer_ownership = True
    permission = {'role': role, 'type': 'user', 'emailAddress': email}
    permission = service.permissions().create(
        transferOwnership=transfer_ownership, body=permission, fileId=item_id
    ).execute()
    return permission

#def transfer_owner(file_id: str, email: str):
#    service = _get_drive_service()
#    permission = {'role': 'owner', 'type': 'user', 'emailAddress': email}
#    permission = service.permissions().create(transferOwnership=True, body=permission, fileId=file_id).execute()

def list_of_items_in_folder(folder_id):
    query = "'{}' in parents".format(folder_id)
    try:
        service = _get_drive_service()
        results = service.files().list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType, parents)").execute()
        items = results.get('files', [])
        page_token = results.get('nextPageToken')
    except Exceprion as exc:
        #print(exc)
        raise Exception('Нет доступа к папке с шаблоном или сервис google недоступен!')
    while True:
        if page_token != None:
            results = service.files().list(pageSize=1000,
                                             pageToken=page_token,
                                             fields="nextPageToken, files(id, name, mimeType)").execute()
            items.extend(results.get('files', []))
            page_token = results.get('nextPageToken')
        else:
            break
    return items

def copy_item(item_id: str, name: str, to_folder_id: str):
    try:
        service = _get_drive_service()
        copy = service.files().copy(fileId=item_id,
                                  body={'parents': [to_folder_id],
                                        'name': name}).execute()
        #transfer_owner_task.delay(file_id=copy['id'], email=Owner.objects.get().email)
        return copy
    except Exception as exc:
        raise Exception('Файл "{}" не удалось скопировать.'.format(name))

def delete_item(item_id: str):
    service = _get_drive_service()
    service.files().delete(fileId=item_id).execute()

def create_item(body: dict):
    service = _get_drive_service()
    return service.files().create(body=body).execute()
    












