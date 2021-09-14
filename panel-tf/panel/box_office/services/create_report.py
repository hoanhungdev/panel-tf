import traceback
from datetime import datetime
from startpage.services.constants import months_full_names

from google_apis.services.spreadsheets.main import \
        get_spreadsheet_rows, write_to_sheet, add_rows, delete_rows, \
        clear_sheet_range, convert_sheets_date_to_datetime
from google_apis.services.drive.main import copy_item, list_of_items_in_folder, \
    create_item
from google_apis.tasks import give_permission_task
from moysklad.services.entities.customentity import get_customentity_documents, \
    create_customentity_document
from moysklad.services.entities.base import get_document_by_id, update_document
from box_office.services.constants import ao_customentity_id, \
    get_body_for_write_report, report_document_sheet_id
from box_office.services.main import get_tf_box_office_id, \
    get_all_box_office
from bitrix.services.main import copy_task

from box_office.models import InputData, Permission



def proceed_all_box_office():
    all_box_office = get_all_box_office()
    for bo in all_box_office:
        proceed_box_office(box_office=bo)

def proceed_box_office(box_office):
    now = datetime.now()
    ao_pattern = f'{now.strftime("%y")}-'
    ao = get_document_by_id(
        doc_type='customentity', 
        id=ao_customentity_id, 
        attributes=[f'search={ao_pattern}']
    )
    new_ao_name = ao_pattern + str(ao['meta']['size'] + 1)
    new_ao_desc = f'{box_office["name"]}'
    body = {
        'name': new_ao_name,
        'description': new_ao_desc
    }
    new_ao = create_customentity_document(
        customentity_id=ao_customentity_id, body=body
    )

    spreadsheet_id = box_office['attribute_value'][39:83]
    rows = get_spreadsheet_rows(
        spreadsheet_id=spreadsheet_id, sheet='РАЗБОР', 
        value_render_option='FORMULA'
    )
    rows_as_formatted_values = get_spreadsheet_rows(
        spreadsheet_id=spreadsheet_id, sheet='РАЗБОР', 
    )
    column_indexes(rows=rows)
    payments_from_tf = []
    rows_in_process = []
    rows_standby = []
    global row
    if box_office.get('entity_type') == 'organization':
        for id, row in enumerate(rows[first_string_index:]):
            if not _is_order_empty():
                rows_in_process.append(row)
            else:
                rows_standby.append(row)
        for id, row in enumerate(rows_in_process):
            search_phrase = 'edit?id='
            doc_id_index = row[order_column].index(search_phrase) + len(search_phrase)
            doc_id = row[order_column][doc_id_index:doc_id_index + 36]
            if row[order_column].count('cashout') == 1:
                _write_report(doc_type='cashout', doc_id=doc_id, ao=new_ao)
            else:
                _write_report(doc_type='cashin', doc_id=doc_id, ao=new_ao)
            try:
                rows_in_process[id][ao_column] = _get_ao_link(ao=new_ao)
            except IndexError:
                rows_in_process[id].insert(ao_column, _get_ao_link(ao=new_ao))
    else:
        for id, row in enumerate(rows[first_string_index:]):
            if not _is_order_empty() and not _is_vozvrat_empty():
                if str(row[order_column]) == '0' or \
                        str(row[vozvrat_column]) == '0':
                    payments_from_tf.append(row)
                else:
                    rows_in_process.append(row)
            else:
                rows_standby.append(row)
        for id, row in enumerate(rows_in_process):
            search_phrase = 'edit?id='
            cashout_id_index = row[order_column].index(search_phrase) + len(search_phrase)
            cashout_id = row[order_column][cashout_id_index:cashout_id_index + 36]
            cashin_id_index = row[vozvrat_column].index(search_phrase) + len(search_phrase)
            cashin_id = row[vozvrat_column][cashin_id_index:cashin_id_index + 36]
            _write_report(doc_type='cashout', doc_id=cashout_id, ao=new_ao)
            _write_report(doc_type='cashin', doc_id=cashin_id, ao=new_ao)
            try:
                rows_in_process[id][ao_column] = _get_ao_link(ao=new_ao)
            except IndexError:
                rows_in_process[id].insert(ao_column, _get_ao_link(ao=new_ao))
    if len(rows_in_process) == 0: raise Exception('Нет платежей для создания А/О!')
    for id, row in enumerate(payments_from_tf):
        try:
            payments_from_tf[id][ao_column] = ''
        except IndexError:
            payments_from_tf[id].insert(ao_column, '')
    rows_in_process += payments_from_tf
    for id, row in enumerate(rows_in_process):
        if rows_in_process[id][data_column]:
            date = convert_sheets_date_to_datetime(
                date=int(rows_in_process[id][data_column])
            )
        else:
            date = ''
        rows_in_process[id][data_column] = date
    rows_in_process.sort(key=lambda row: row[data_column])
    processed_rows = []
    for id, month in enumerate(months_full_names):
        payments = []
        for pid, pay in enumerate(rows_in_process):
            try:
                if int(rows_in_process[pid][data_column].month) == id+1:
                    payments.append(pay)
            except AttributeError:
                data = datetime.strptime(rows_in_process[pid][data_column], '%d.%m.%Y')
                if int(data.month) == id+1:
                    payments.append(pay)
        if not payments: continue
        for pay_id, row in enumerate(payments):
            payments[pay_id][data_column] = row[data_column].strftime('%d.%m.%Y')
        month_rows = get_spreadsheet_rows(spreadsheet_id, sheet=month)
        month_rows += [[], [], [], []] # необходимо на случай, если есть только названия столбцов
        empty_rows_together = 0
        for row_id, row in enumerate(month_rows):
            if not is_amounts_valid(write_error=False) and \
                    _is_order_empty() and row_id > 4:
                empty_rows_together += 1
                if empty_rows_together > 4:
                    write_to_sheet(
                        spreadsheet_id=spreadsheet_id, sheet=month, 
                        column='A', row_id=row_id + 1 - empty_rows_together + 1, 
                        data=payments
                    )
                    processed_rows += payments
                    break
            else:
                empty_rows_together = 0
    if len(rows_in_process) != len(processed_rows):
        raise Exception('Есть неучтенные платежи!')
    folders_for_reports = InputData.objects.get(title='Папка для АО').value
    report_years = list_of_items_in_folder(folder_id=folders_for_reports)
    destination_folder = [y for y in report_years if y['name'] == str(now.year)]
    if len(destination_folder) == 0:
        body = {
            'name': f'{now.year}',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folders_for_reports]
        }
        destination_folder = create_item(body=body)
    elif len(destination_folder) == 1:
        destination_folder = destination_folder[0]
    elif len(destination_folder) > 1:
        raise Exception('Несколько папок с ао для текущего года!')
    report_document = copy_item(
        item_id=InputData.objects.get(title='Шаблон АО сотрудника').value,
        to_folder_id=destination_folder['id'], 
        name=f'{box_office["name"]} {now.day}.{now.month}.{now.year}'
    )
    for perm in Permission.objects.all():
        give_permission_task(
            item_id=report_document['id'], email=perm.email, 
            role=perm.role
        )
    for id, row in enumerate(rows_in_process):
        rows_in_process[id] = rows_in_process[id][prihod_column:ao_column+1]
        rows_in_process[id].pop(statya_rashodov_column)
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='РАЗБОР', 
        start=f'A{first_string_index+1}', finish=f'ZZZ1000'
    )
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='РАЗБОР', 
        column='A', row_id=first_string_index+1, data=rows_standby
    )
    add_rows(
        spreadsheet_id=report_document['id'], range='Лист1!B7', 
        data=rows_in_process
    )
    write_to_sheet(
        spreadsheet_id=report_document['id'], sheet='Лист1', 
        column='E', row_id=3, data=f'{now.day}.{now.month}.{now.year}'
    )
    write_to_sheet(
        spreadsheet_id=report_document['id'], sheet='Лист1', 
        column='G', row_id=3, data=f'{new_ao_name}'
    )
    write_to_sheet(
        spreadsheet_id=report_document['id'], sheet='Лист1', 
        column='I', row_id=9 + len(rows_in_process), 
        data=f'{box_office["name"]}'
    )
    write_to_sheet(
        spreadsheet_id=report_document['id'], sheet='Лист1', 
        column='I', row_id=19 + len(rows_in_process), 
        data=f'{box_office["name"]}'
    )
    delete_rows(
        spreadsheet_id=report_document['id'], 
        sheet_id=report_document_sheet_id,
        start_index=5, 
        end_index=6
    )
    delete_rows(
        spreadsheet_id=report_document['id'], 
        sheet_id=report_document_sheet_id,
        start_index=5 + len(rows_in_process), 
        end_index=6 + len(rows_in_process)
    )
    rows_after_changes = get_spreadsheet_rows(
        spreadsheet_id=spreadsheet_id, sheet='РАЗБОР'
    )
    spreadsheet_base_url = 'https://docs.google.com/spreadsheets/d/'
    add_to_description = f'\nСсылка на отчёт: {spreadsheet_base_url + report_document["id"]}'
    task_id = InputData.objects.get(title='Шаблонная задача на подписание отчета').value
    if rows_as_formatted_values[ostatok_row][ostatok_column] == rows_after_changes[ostatok_row][ostatok_column]:
        copy_task(
            id=task_id, add_to_title=new_ao_desc, 
            add_to_description=add_to_description
        )
    else: # в случае ошибки в цифрах ставлю задачу себе с пометкой "ошибка"
        copy_task(
            id=task_id, add_to_title=f'{new_ao_desc} ОШИБКА!', responsible_id=165,
            add_to_description=add_to_description
        )
        
        




def is_prihod_empty(write_error: bool):
    try:
        prihod = str(row[prihod_column]).replace(' ', '')
    except IndexError:
        return True
    if prihod == '':
        if write_error:
            _write_error(text='Поле ПРИХОД пустое!')
        return True
    else:
        return False
        
def is_rashod_empty(write_error: bool):
    try:
        rashod = str(row[rashod_column]).replace(' ', '')
    except IndexError:
        return True
    if rashod == '':
        if write_error:
            _write_error(text='Поле РАСХОД пустое!')
        return True
    else:
        return False

def is_amounts_valid(write_error: bool):
    """Проверка валидности сумм"""
    if is_prihod_empty(write_error=False) and \
            is_rashod_empty(write_error=False):
        if write_error:
            _write_error(text='Поля ПРИХОД и РАСХОД пустые!')
        return False
    elif not is_prihod_empty(write_error=False) and \
            not is_rashod_empty(write_error=False):
        if write_error:
            _write_error(text='Поля ПРИХОД и РАСХОД заполнены одновременно!')
        return False
    else:
        return True

def _get_ao_link(ao: dict):
    some_id = '311d7d49-b208-11e6-7a31-d0fd0001b08d'
    link = f'https://online.moysklad.ru/app/#finance?{some_id}=' \
        f'[{ao["id"]}\\,{ao["name"]}\\,\\,CustomEntity],equals'
    return f'''=ГИПЕРССЫЛКА("{link}";"{ao["name"]}")'''

def _write_report(doc_type: str, doc_id: str, ao: dict):
    body = get_body_for_write_report(doc_type=doc_type)
    body['attributes'][0]['value']['meta'] = ao['meta']
    return update_document(doc_type=doc_type, body=body, doc_id=doc_id)

def _is_order_empty():
    try:
        order = str(row[order_column]).replace(' ', '')
    except IndexError:
        return True
    if order == '':
        return True
    else:
        return False

def _is_vozvrat_empty():
    try:
        vozvrat = str(row[vozvrat_column]).replace(' ', '')
    except IndexError:
        return True
    if vozvrat == '':
        return True
    else:
        return False

def column_indexes(rows: list):
    """Функция динамически определяет номера колонок"""
    for id, row in enumerate(rows):
        if row.count('ТЕКУЩИЙ ОСТАТОК'):
            global ostatok_column, ostatok_row
            ostatok_row = id
            ostatok_column = row.index('ТЕКУЩИЙ ОСТАТОК') + 1
        if row.count('ПРИХОД') != 0:
            global first_string_index
            first_string_index = id + 1
            global prihod_column
            prihod_column = row.index('ПРИХОД')
            global rashod_column
            rashod_column = row.index('РАСХОД')
            global contragent_column
            contragent_column = row.index('КОНТРАГЕНТ')
            global project_column
            project_column = row.index('ПРОЕКТ')
            global priemka_column
            priemka_column = row.index('ПРИЕМКА')
            global zakaz_column
            zakaz_column = row.index('ЗАКАЗ')
            global commentariy_column
            commentariy_column = row.index('КОММЕНТАРИЙ')
            global statya_rashodov_column
            statya_rashodov_column = row.index('СТАТЬЯ РАСХОДОВ')
            global data_column
            data_column = row.index('ДАТА')
            global order_column
            order_column = row.index('ОРДЕР')
            global vozvrat_column
            vozvrat_column = row.index('ВОЗВРАТ')
            global ao_column
            ao_column = row.index('А/О')
            global doc_column
            doc_column = row.index('ДОК')
            global control_column
            control_column = row.index('КОНТРОЛЬ')
            break


