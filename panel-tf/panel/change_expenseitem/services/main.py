import traceback

from change_expenseitem.services.base import spreadsheet_id, sheet
from google_apis.services.spreadsheets.main import get_spreadsheet_rows, \
    write_to_sheet
from moysklad.services.entities.base import get_document, get_documents, \
    update_documents


class InputData:
    def __init__(
            self, expenseitem_name: str, agent_name: str, 
            first_operator: str, project_name: str, second_operator: str, 
            comment: str):
        self.expenseitem_meta = get_document(
            doc_type='expenseitem', filters=[f'name={expenseitem_name}']
        )['meta']
        if agent_name:
            self.agent_href = get_document(
                doc_type='counterparty', filters=[f'name={agent_name}']
            ).get('meta', {}).get('href', '')
        else:
            self.agent_href = ''
        self.first_operator = _unify_user_str(first_operator)
        if project_name:
            self.project_href = get_document(
                doc_type='project', filters=[f'name={project_name}']
            ).get('meta', {}).get('href', '')
        else:
            self.project_href = ''
        self.second_operator = _unify_user_str(second_operator)
        self.comment = _unify_user_str(comment)

def start():
    try:
        rows = get_spreadsheet_rows(spreadsheet_id=spreadsheet_id, sheet=sheet)
        _column_indexes(rows=rows)
        inputs = []
        
        for row_id, row in enumerate(rows[first_string_index:]):
            try:
                contragent = row[contragent_column]
            except:
                contragent = ''
            try:
                operator_1 = row[operator_1_column]
                proekt = row[proect_column]
            except:
                operator_1 = ''
                proekt = ''
            try:
                operator_2 = row[operator_2_column]
                commentariy = row[commentariy_column]
            except:
                operator_2 = ''
                commentariy = ''
            if _is_row_valid(row=row):
                inputs.append(InputData(
                    expenseitem_name=row[statya_rashodov_column],
                    agent_name=contragent,
                    first_operator=operator_1,
                    project_name=proekt,
                    second_operator=operator_2,
                    comment=commentariy,
                ))
            else:
                _write_error(text='Укажите Статью расхода и контрагента/проект!')
        for input_data in inputs:
            _proceed(input_data=input_data)
    except IndexError:
        print(traceback.format_exc())
        _write_error(text='Укажите Статью расхода!')
    except:
        print(traceback.format_exc())
        _write_error(text='Неизвестная ошибка, сообщите администратору!')
    
def _proceed(input_data: InputData):
    docs = []
    docs_by_project = []
    if input_data.agent_href:
        agent_filter = [f'agent={input_data.agent_href}']
        docs = _get_documents(filters=agent_filter)
    if input_data.project_href:
        project_filter = [f'project={input_data.project_href}']
        docs_by_project = _get_documents(filters=project_filter)
        if input_data.agent_href:
            if input_data.first_operator == 'и':
                docs = [doc for doc in docs if doc in docs_by_project]
            elif input_data.first_operator == 'или':
                    docs += docs_by_project
            elif input_data.first_operator == 'ине':
                docs = [doc for doc in docs if doc not in docs_by_project]
        else:
            docs += docs_by_project
    # далее фильтр по комментарию
    comment = input_data.comment
    if comment:
        if input_data.second_operator == 'и':
            docs = [doc for doc in docs if comment in _unify_user_str(doc.get('description', ''))]
        elif input_data.second_operator == 'или':
            _write_error(text='Недопустимое значение поля "Оператор 2!"')
            raise
        elif input_data.second_operator == 'ине':
            docs = [doc for doc in docs if comment not in _unify_user_str(doc.get('description', ''))]
    elif not comment and input_data.second_operator:
        if input_data.second_operator == 'и':
            docs = [doc for doc in docs if _unify_user_str(doc.get('description', '')) == comment]
        elif input_data.second_operator == 'или':
            _write_error(text='Недопустимое значение поля "Оператор 2!"')
            raise
        elif input_data.second_operator == 'ине':
            docs = [doc for doc in docs if _unify_user_str(doc.get('description', '')) != comment]
    _change_expenseitem(docs=docs, expenseitem_meta=input_data.expenseitem_meta)
    _write_error(text='')

def _change_expenseitem(expenseitem_meta: dict, docs: list):
    for doc in docs:
        doc['expenseItem'] = {'meta': expenseitem_meta}
    cashouts = [doc for doc in docs if doc['meta']['type'] == 'cashout']
    paymentouts = [doc for doc in docs if doc['meta']['type'] == 'paymentout']
    if cashouts:
        update_documents(doc_type='cashout', body=cashouts)
    if paymentouts:
        update_documents(doc_type='paymentout', body=paymentouts)
    
def _get_documents(filters: list):
    docs = []
    docs += get_documents(
        doc_type='cashout', 
        filters=filters
        )
    docs += get_documents(
        doc_type='paymentout', 
        filters=filters
    )
    return docs

def _is_row_valid(row):
    try:
        contragent = row[contragent_column].replace(' ', '')
    except:
        return False
    try:
        proekt = row[proect_column].replace(' ', '')
    except:
        return False
    if row[statya_rashodov_column].replace(' ', '') != '' and \
            (
                contragent != '' or \
                proekt != ''
            ):
        return True
    return False

def _unify_user_str(data: str):
    return data.replace(' ', '').lower()

def _write_error(text: str):
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet=sheet,
        column=oshibki_column, row_id=first_string_index+1, data=text)

def _column_indexes(rows: list):
    """Функция динамически определяет номера колонок"""
    for id, row in enumerate(rows):
        if row.count('Статья расходов') != 0:
            global first_string_index
            first_string_index = id + 1
            global statya_rashodov_column
            statya_rashodov_column   = row.index('Статья расходов')
            global contragent_column
            contragent_column = row.index('Контрагент')
            global operator_1_column
            operator_1_column = row.index('Оператор 1')
            global proect_column
            proect_column = row.index('Проект')
            global operator_2_column
            operator_2_column = row.index('Оператор 2')
            global commentariy_column
            commentariy_column = row.index('Комментарий')
            global oshibki_column
            oshibki_column = commentariy_column + 1
            break






