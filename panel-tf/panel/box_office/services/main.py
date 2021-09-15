import traceback
from datetime import datetime

from moysklad.services.entities.organization import \
        get_organizations_name_with_attribute_value
from moysklad.services.entities.employee import \
        get_employees_name_with_attribute_value, \
        get_employees_name_and_meta
from moysklad.services.entities.base import \
        create_document, get_document, \
        get_documents
from moysklad.services.base import MoyskladException, \
        MoyskladDocumentNotFoundException, MoyskladFewDocumentsFoundException
from google_apis.services.spreadsheets.main import \
        get_table_name, get_spreadsheet_rows, write_to_sheet
from summary_table.services.sheets.vzaimoraschety import get_end_balance

from box_office.services.constants import ao_meta, organization_meta, \
        project_for_cashout, expenseitem_for_cashout, body_cashout, \
        body_cashin, default_expenseitem



class BoxOfficeDataIntegrityAffectedException(Exception):
    pass
class BoxOfficeProjectClosedException(Exception):
    pass

def proceed_all():
    """Создание ордеров в мойсклад по всем кассам"""
    all_box_office = get_all_box_office()
    #all_box_office = [{'name': 'тест касса тф', 'attribute_value': 'https://docs.google.com/spreadsheets/d/1IQjVJDighBbcFA8fD_3h6vyhxLKGLn8h-7p_mYp96Ms/edit#gid=1890343792', 'entity_type': 'organization', 'entity_id': 'b66837ad-d66c-11e6-7a69-9711004b5836'}]
    global box_office, tf_box_office_id
    tf_box_office_id = get_tf_box_office_id(all_box_office=all_box_office)
    for bo_id, box_office in enumerate(all_box_office):
        try:
            _proceed()
        except:
            Error.objects.create(title='Непредвиденная ошибка!', traceback=traceback.format_exc())

def proceed_single(bo_link):
    """Создание ордеров в мойсклад по одной кассе"""
    all_box_office = get_all_box_office()
    global box_office, tf_box_office_id
    box_office = [bo for bo in all_box_office if bo.get('attribute_value', '')[39:83] == bo_link[39:83]][0]
    tf_box_office_id = get_tf_box_office_id(all_box_office=all_box_office)
    _proceed()

def _create_return_cashin():
    if _is_vozvrat_empty():
        if spreadsheet_id == tf_box_office_id: # если касса тф
            if _is_order_created(write_error=False):
                if _is_doc_handed():
                    _write_return_doc()
        else: # касса сотрудника
            if not is_prihod_empty(write_error=False):
                _write_return_doc()
            elif not is_rashod_empty(write_error=False):
                if _is_order_created(write_error=False):
                    if _is_doc_handed():
                        cashin = _create_return_cashin_in_moysklad()
                        _write_success(
                            response=cashin, column=vozvrat_column
                        )

def _write_end_balance(emp_id: str):
    end_balance = get_end_balance(emp_id=emp_id)
    try:
        write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
            column=2, row_id=3, data='Остаток в МС')
        write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
            column=3, row_id=3, data=end_balance)
    except Exception as exc:
        print(exc)

def _create_return_cashin_in_moysklad():
    body = {}
    body['sum'] = amount
    body['agent'] = {"meta" : {
        "href" : f"https://online.moysklad.ru/api/remap/1.2/entity/employee/{box_office['entity_id']}",
        "type" : "employee"
    }}
    body['organization'] = {'meta': organization_meta}
    body['description'] = comment
    body['attributes'] = body_cashin['attributes']
    body['attributes'][0]['value']['meta'] = ao_meta
    return create_document(doc_type='cashin', body=body)

def _proceed():
    global spreadsheet_id
    spreadsheet_id = box_office['attribute_value'][39:83]
    _write_end_balance(emp_id=box_office['entity_id'])
    table_name = box_office['name']
    rows = get_spreadsheet_rows(spreadsheet_id, sheet='РАЗБОР')
    column_indexes(rows)
    breakpoint = 0
    global row_id, row
    for row_id, row in enumerate(rows[first_string_index:]):
        print(row)
        # необходимо для записи в верную строку
        row_id += first_string_index + 1
        if len(row) < 3 or \
                (len(row) > 2 and not is_amounts_valid(write_error=False)):
            breakpoint += 1
            # если встречается 2 пустые строки подряд, то дальше не иду
            if breakpoint > 2:
                break
        else:
            global comment, amount, expenseitem
            amount = _get_amount()
            comment = _get_comment(table_name=table_name)
            try:
                expenseitem = row[statya_rashodov_column]
            except:
                expenseitem = ''
            expenseitem = _get_expenseitem(name=expenseitem)
            print(row)
            _proceed_row() # основной алгоритм
            rows = get_spreadsheet_rows(spreadsheet_id, sheet='РАЗБОР')
            _create_return_cashin() # создание возвратов

def _proceed_row():
    employee_meta = _get_employee_or_organization_meta()
    if employee_meta and _is_row_valid():
        # валидация, а так же разветвление алгоритма
        if spreadsheet_id == tf_box_office_id: # если касса ТФ
            if not is_prihod_empty(write_error=False): # приход
                cashin = _create_cashin(
                    counterparty_meta=employee_meta, amount=amount, 
                    comment=comment
                )
                _write_success(column=order_column, response=cashin)
            elif not is_rashod_empty(write_error=False): # расход
                cashout = _create_cashout(
                    counterparty_meta=employee_meta, amount=amount, 
                    comment=comment, expenseitem=expenseitem
                )
                _write_success(column=order_column, response=cashout)
    elif _is_row_valid() and \
            not _is_proekt_empty(write_error=True) and \
            _is_priemka_or_zakaz_filled(write_error=True):
        # валидация
        project = _get_project(name=row[project_column])
        counterparty_meta = _get_counterparty_or_organization_meta(name=row[contragent_column])
        if project and counterparty_meta:
            if not _is_zakaz_empty(write_error=False) and not is_prihod_empty(write_error=False): # приход
                operation = _get_operation(
                    doc_type='customerorder', name=row[zakaz_column], 
                    project_meta=project['meta'], 
                    counterparty_meta=counterparty_meta
                )
            elif not _is_priemka_empty(write_error=False) and not is_rashod_empty(write_error=False): # расход
                operation = _get_operation(
                    doc_type='supply', name=row[priemka_column], 
                    project_meta=project['meta'], 
                    counterparty_meta=counterparty_meta
                )
            elif not _is_zakaz_empty(write_error=False) and not is_rashod_empty(write_error=False): # расход
                operation = _get_operation(
                    doc_type='purchaseorder', name=row[zakaz_column], 
                    project_meta=project['meta'], 
                    counterparty_meta=counterparty_meta
                )
            if not operation:
                if not _is_priemka_empty(write_error=False):
                    _write_error(text=f'Не найдена приемка №{row[priemka_column]}')
                elif not _is_zakaz_empty(write_error=False):
                    _write_error(text=f'Не найден заказ №{row[zakaz_column]}')
            if operation:
                if not is_prihod_empty(write_error=False): # приход
                    cashin = _create_cashin_with_operation(
                        counterparty_meta=counterparty_meta, amount=amount,
                        comment=comment, operation_meta=operation['meta'], 
                        project=project
                    )
                    _write_success(column=order_column, response=cashin)
                if not is_rashod_empty(write_error=False): # расход
                    if expenseitem:
                        cashout = _create_cashout_with_operation(
                            counterparty_meta=counterparty_meta, 
                            amount=amount, comment=comment, 
                            operation_meta=operation['meta'], 
                            project=project, expenseitem=expenseitem
                        )
                        _write_success(column=order_column, response=cashout)

def _write_return_doc(data=0, write_order=False):
    if write_order:
        write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
            column=order_column, row_id=row_id, data=data)
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
        column=vozvrat_column, row_id=row_id, data=data)
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
        column=control_column, row_id=row_id, data='')

def _is_doc_handed(write_error=True):
    """
    Проверка ячейки со статусом подтверждающих документов. 
    Истина, если документ сдан или не требуется, иначе Ложь.
    """
    try:
        doc = row[doc_column].replace(' ', '')
        doc = doc.lower()
    except:
        doc = ''
    if doc == 'сданы' or doc == 'нетребуется' or doc == 'сдан':
        return True
    else:
        if write_error:
            _write_error(text='Сдайте документы подтверждающие расход!')
        return False

def _is_vozvrat_empty():
    try:
        vozvrat = row[vozvrat_column].replace(' ', '')
    except IndexError:
        return True
    if vozvrat == '':
        return True
    else:
        return False

def _is_priemka_or_zakaz_filled(write_error: bool):
    if not _is_priemka_empty(write_error=False) or \
            not _is_zakaz_empty(write_error=False):
        return True
    if write_error:
        _write_error(text='Не заполнено поле ПРИЕМКА или ЗАКАЗ')
    return False

def _is_row_valid():
    if is_amounts_valid(write_error=False) and \
            not _is_order_created(write_error=False):
        if not _is_agent_empty(write_error=True):
            return True
    return False

def get_tf_box_office_id(all_box_office: list):
    """
    Функция принимает массив всех касс, ищет кассу
    с именем в "Техно Фасад" (имя организации из моегосклада)
    и возвращает её
    """
    box_office_iterator = iter(bo1['attribute_value'][39:83] for bo1 in all_box_office if bo1['entity_type'] == 'organization')
    tf_box_office_id = next(box_office_iterator, None)
    return tf_box_office_id

def _get_employee_or_organization_meta():
    """
    Ищет сотрудника (юр.лицо) с именем как у контрагента,
    если нет такого сотрудника (юр.лица), то возвращает None
    """
    employees = get_employees_name_and_meta()
    employees_iterator = iter(emp['meta'] for emp in employees if emp['name'] == row[contragent_column])
    employee_meta = next(employees_iterator, None)
    if not employee_meta:
        try:
            organization = get_document(doc_type='organization', 
                filters=[f'name={row[contragent_column]}']
            )
            return organization.get('meta')
        except:
            return None
    else:
        return employee_meta

def _get_comment(table_name: str):
    try:
        comment = row[commentariy_column] + f' | {table_name}'
    except IndexError:
        comment = ' ' + f'| {table_name}'
    return comment

def _get_expenseitem(name: str):
    if not name:
        #_write_error(text='Не указана статья расходов!')
        return default_expenseitem
    try:
        expenseitem = get_document(doc_type='expenseitem', 
            filters=[f'name={name}']
        )
    except MoyskladDocumentNotFoundException:
        #_write_error(text='Не найдена статья расходов!')
        return default_expenseitem
    except MoyskladFewDocumentsFoundException:
        #_write_error(text='Найдено несколько статей расхода!')
        return default_expenseitem
    except MoyskladException:
        #_write_error('Ошибка запроса в МойСклад')
        return default_expenseitem
    return expenseitem

def _get_operation(doc_type: str, name: str, project_meta: dict,
        counterparty_meta: dict):
    try:
        document = get_document(doc_type=doc_type,
            filters=[f'name~{name}', f'agent={counterparty_meta["href"]}', 
                f'project={project_meta["href"]}']
        )
    except MoyskladException:
        _write_error(text=f'Ошибка запроса в МойСклад!')
        return
    except MoyskladDocumentNotFoundException:
        _write_error(text=f'Не найден документ для привязки!')
        return
    except MoyskladFewDocumentsFoundException:
        _write_error(text=f'Найдено несколько документов для привязки!')
        return
    return document

def _create_cashout_with_operation(counterparty_meta: dict,
        amount: int, comment: str,
        operation_meta: dict, project: dict,
        expenseitem: dict):
    body = body_cashout.copy()
    if not _is_date_empty():
        moment = datetime.strptime(row[data_column], '%d.%m.%Y')
        body['moment'] = _get_date_for_moysklad(date=moment)
    body['agent']['meta'] = counterparty_meta
    body['project']['meta'] = project['meta']
    body['sum'] = amount
    body['attributes'][0]['value']['meta'] = ao_meta
    body['description'] = comment
    body['expenseItem']['meta'] = expenseitem['meta']
    body['operations'][0]['meta'] = operation_meta
    body['operations'][0]['linkedSum'] = amount
    return create_document(doc_type='cashout', body=body)
    
def _create_cashin_with_operation(counterparty_meta: dict,
        amount: int, comment: str,
        operation_meta: dict, project: dict):
    body = body_cashin.copy()
    if not _is_date_empty():
        moment = datetime.strptime(row[data_column], '%d.%m.%Y')
        body['moment'] = _get_date_for_moysklad(date=moment)
    body['agent']['meta'] = counterparty_meta
    body['project']['meta'] = project['meta']
    body['sum'] = amount
    body['attributes'][0]['value']['meta'] = ao_meta
    body['description'] = comment
    body['operations'][0]['meta'] = operation_meta
    body['operations'][0]['linkedSum'] = amount
    return create_document(doc_type='cashin', body=body)

def _get_counterparty_or_organization_meta(name: str):
    try:
        counterparties = get_documents(doc_type='counterparty', 
            filters=[f'name~{name}']
        )
        if len(counterparties) > 1:
            try:
                counterparty = get_document(doc_type='counterparty', 
                    filters=[f'name={name}']
                )
            except MoyskladException:
                _write_error(text='Ошибка запроса в МойСклад!')
                return
            except MoyskladDocumentNotFoundException:
                _write_error(text='Не найден контрагент!')
                return
            except MoyskladFewDocumentsFoundException:
                _write_error(text='Найдено больше одного контрагента!')
                return
            return counterparty['meta']
        elif len(counterparties) < 1:
            raise MoyskladDocumentNotFoundException
    except MoyskladDocumentNotFoundException:
        _write_error(text='Не найден контрагент!')
        return
    return counterparties[0]['meta']
    
    
def _get_project(name: str):
    """Поиск проекта, а так же его валидация"""
    if _is_proekt_empty(write_error=True):
        return
    try:
        project = get_document(doc_type='project', filters=[f'name~{name}'])
    except MoyskladDocumentNotFoundException:
        _write_error(text='Не найден проект!')
        print(traceback.format_exc())
        return
    except MoyskladFewDocumentsFoundException:
        _write_error(text='Найдено несколько пректов!')
        return
    except MoyskladException:
        _write_error('Ошибка запроса в МойСклад!')
        return
    for attr in project['attributes']:
        # аттрибут "Проект закрыт"
        if attr['id'] == '03ecc5ba-62bf-11e8-9109-f8fc00000eca':
            is_project_closed = attr['value']
            if is_project_closed:
                _write_error(text='Проект закрыт! Необходимо согласование.')
                return
    return project

def _create_cashout(counterparty_meta: dict,
        amount: int, comment: str ,expenseitem, dict):
    body = body_cashout.copy()
    if not _is_date_empty():
        moment = datetime.strptime(row[data_column], '%d.%m.%Y')
        body['moment'] = _get_date_for_moysklad(date=moment)
    body['agent']['meta'] = counterparty_meta
    body['sum'] = amount
    body['attributes'][0]['value']['meta'] = ao_meta
    body['description'] = comment
    body['expenseItem']['meta'] = expenseitem['meta']
    body.pop('operations')
    return create_document(doc_type='cashout', body=body)
    
def _create_cashin(counterparty_meta: dict,
        amount: int,
        comment: str):
    body = body_cashin.copy()
    if not _is_date_empty():
        moment = datetime.strptime(row[data_column], '%d.%m.%Y')
        body['moment'] = _get_date_for_moysklad(date=moment)
    body['agent']['meta'] = counterparty_meta
    body['sum'] = amount
    body['attributes'][0]['value']['meta'] = ao_meta
    body['description'] = comment
    body.pop('operations')
    body.pop('project')
    return create_document(doc_type='cashin', body=body)
    
    
def _get_amount():
    """
    Принимает сумму форматированную гугл таблицами
    возвращает сумму в копейках для передачи в мойсклад
    """
    if not is_prihod_empty(write_error=False):
        amount = row[prihod_column]
    elif not is_rashod_empty(write_error=False):
        amount = row[rashod_column]
    amount = amount.replace(u'\xa0', u'').replace(' ', '')
    try:
        comma_index = amount.index(',')
    except ValueError:
        return int(f'{amount}00')
    amount_cents = amount[comma_index+1:]
    if len(amount_cents) == 1:
        amount_cents += '0'
    amount = int(f'{amount[:comma_index]}{amount_cents}')
    return amount

def _get_date(date=''):
    if date:
        date = f'{date.strftime("%d")}.{date.strftime("%m")}.{date.strftime("%Y")}'
    else:
        now = datetime.now()
        date = f'{now.strftime("%d")}.{now.strftime("%m")}.{now.strftime("%Y")}'
    return date
    
def _get_date_for_moysklad(date):
    date = f'{date.strftime("%Y")}-{date.strftime("%m")}-{date.strftime("%d")} ' \
        f'{date.strftime("%H")}:{date.strftime("%M")}:{date.strftime("%S")}'
    return date
   
def _write_error(text: str):
    if _is_date_empty():
        write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
            column=data_column, row_id=row_id, data=_get_date())
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
            column=control_column, row_id=row_id, data=text)
    
def _write_success(response: dict, column: int):
    order = f'''=ГИПЕРССЫЛКА("{response['meta']['uuidHref']}";"{response['name']}")'''
    while(True):
        try:
            row[order_column] = order
            break
        except:
            row.append('')
    if _is_date_empty():
        write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
            column=data_column, row_id=row_id, data=_get_date())
    
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
            column=column, row_id=row_id, data=order)
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet='РАЗБОР',
            column=control_column, row_id=row_id, data='')

def _is_order_created(write_error: bool):
    """
    функция принимает строку таблицы,
    возвращает истину, если платеж создан
    и ложь, если платеж не создан
    """
    try:
        if row[order_column].replace(' ', '') == '':
            return False
        else:
            if write_error:
                _write_error(text='Поле ОРДЕР заполнено!')
            return True
    except IndexError: # строка короткая, колонка ордера тоже пустая
        return False

def _is_date_empty():
    try:
        data = row[data_column].replace(' ', '')
    except IndexError:
        return True
    if data == '':
        return True
    else:
        return False

def is_prihod_empty(write_error: bool):
    try:
        prihod = row[prihod_column].replace(' ', '')
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
        rashod = row[rashod_column].replace(' ', '')
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

def _is_agent_empty(write_error: bool):
    """Проверка пустая ли ячейка с наименованием контрагента"""
    agent = row[contragent_column].replace(' ', '')
    if agent == '':
        if write_error:
            _write_error(text='Поле КОНТРАГЕНТ пустое!')
        return True
    else:
        return False

def _is_proekt_empty(write_error: bool):
    """Проверка пустая ли ячейка с наименованием проекта"""
    project = row[project_column].replace(' ', '')
    if project == '':
        if write_error:
            _write_error(text='Поле КОНТРАГЕНТ пустое!')
        return True
    else:
        return False

def _is_priemka_empty(write_error: bool):
    priemka = row[priemka_column].replace(' ', '')
    if priemka == '':
        if write_error:
            _write_error(text='Поле ПРИЕМКА пустое!')
        return True
    else:
        return False

def _is_zakaz_empty(write_error: bool):
    zakaz = row[zakaz_column].replace(' ', '')
    if zakaz == '':
        if write_error:
            _write_error(text='Поле ЗАКАЗ пустое!')
        return True
    else:
        return False

def column_indexes(rows: list):
    """Функция динамически определяет номера колонок"""
    for id, row in enumerate(rows):
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
    
def get_all_box_office():
    """Возвращает массив всех касс"""
    box_office = get_organizations_name_with_attribute_value(attribute_name='Касса')
    box_office += get_employees_name_with_attribute_value(attribute_name='Касса')
    box_office = [bo for bo in box_office \
        if bo['attribute_value'].startswith('https://docs.google.com/spreadsheets/d/')]
    return box_office

    
    
    