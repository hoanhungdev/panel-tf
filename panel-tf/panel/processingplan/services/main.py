import traceback

from processingplan.services.base import spreadsheet_id, sheet, body
from google_apis.services.spreadsheets.main import get_spreadsheet_rows, \
    write_to_sheet
from moysklad.services.entities.base import get_document, get_documents, \
    create_document, add_materials
from moysklad.services.base import MoyskladException, \
    MoyskladDocumentNotFoundException, MoyskladFewDocumentsFoundException
from moysklad.services.reports.stock import get_report_all


def _get_document(doc_type, filters=[], attributes=[]):
    try:
        return get_document(
            doc_type=doc_type, filters=filters, attributes=attributes
        )
    except MoyskladException:
        _write_error(text='Ошибка при запросе в МС!')
    except MoyskladDocumentNotFoundException:
        _write_error(text='Не найден документ в МС!')
    except MoyskladFewDocumentsFoundException:
        _write_error(text='Найдено несколько документов в МС!')
    

def start():
    rows = get_spreadsheet_rows(spreadsheet_id=spreadsheet_id, sheet=sheet)
    _column_indexes(rows=rows)
    try:
        store_name = rows[first_string_index][store_column]
    except:
        _write_error(text='Укажите Склад!')
    store = _get_document(
        doc_type='store', 
        filters=[f'name={store_name}']
    )
    products = []
    raw_productfolders = []
    for row in rows[first_string_index:]:
        try:
            if row[productfolders_column]:
                raw_productfolders.append(row[productfolders_column])
        except:
            pass
    for id, rpf in enumerate(raw_productfolders):
        pf = _get_document(
            doc_type='productfolder', 
            filters=[f'name={rpf}']
        )
        products_from_report = get_report_all(
            href=store["meta"]["href"],
            filters=[
                f'productFolder={pf["meta"]["href"]}',
                'archived=true',
                'archived=false'
            ]
        )['rows']
        for pid, prod in enumerate(products_from_report):
            products.append({})
            products[pid]['product'] = {'meta': prod['meta']}
            products[pid]['quantity'] = prod['stock']
    if not products:
        _write_error('Укажите хотябы одну Группу!')
    
    body['materials'] = [products.pop(0)]
    body['name'] = store['name']
    processingplan = create_document(doc_type='processingplan', body=body)
    add_materials(
        doc_type='processingplan', 
        doc_id=processingplan['id'], 
        materials=products
    )
    _write_success(processingplan=processingplan)

def _write_success(processingplan: dict):
    link = f'''=ГИПЕРССЫЛКА("{processingplan['meta']['uuidHref']}";"Тех. Карта: {processingplan['name']}")'''
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet=sheet,
        column=errors_column, row_id=first_string_index, data=link)
    _write_error('', raise_exception=False)

def _write_error(text: str, raise_exception=True):
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet=sheet,
        column=errors_column, row_id=first_string_index+1, data=text)
    if raise_exception:
        raise

def _column_indexes(rows: list):
    """Функция динамически определяет номера колонок"""
    for id, row in enumerate(rows):
        if row.count('Склад') != 0:
            global first_string_index
            first_string_index = id + 1
            global store_column
            store_column = row.index('Склад')
            global productfolders_column
            productfolders_column = row.index('Группа')
            global errors_column
            errors_column = productfolders_column + 2
            break





