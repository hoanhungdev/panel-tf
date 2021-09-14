from datetime import datetime, timedelta

from google_apis.services.spreadsheets.main import \
        get_spreadsheet_rows, write_to_sheet, start_date
from moysklad.services.reports.stock import get_report_all
from moysklad.services.entities.base import get_document, create_document
from moysklad.services.base import MoyskladException, \
    MoyskladDocumentNotFoundException, MoyskladFewDocumentsFoundException

from .base import sheet, processed_product_meta

def start(ss_id: str, debit_number=0):
    global spreadsheet_id
    spreadsheet_id = ss_id
    global debit_num
    debit_num = int(debit_number)
    rows = get_spreadsheet_rows(
        spreadsheet_id=spreadsheet_id, 
        sheet=sheet, 
        value_render_option='UNFORMATTED_VALUE'
    )
    column_indexes(rows)
    _write_error('', raise_exception=False)
    try:
        operation_link = rows[first_string_index-2][spisanie_1_column + debit_num*3]
        if operation_link:
            raise
    except:
        _write_error(f'По данному этапу уже создана тех. операция!. Этап №{debit_num+1}.')
    for id, row in enumerate(rows):
        rows[id] = rows[id][:spisanie_1_column + 9*3]
        try:
            nomenklatura = row[nomenklatura_column]
        except:
            nomenklatura = ''
        if nomenklatura == '' and id >= first_string_index: 
            last_string_index = id
            break
    try:
        rows = rows[:last_string_index]
    except: # строки с кривым заполнением внизу таблицы может и не быть
        pass
    try:
        store = get_document(doc_type='store', filters=[f'name={sklad_name}'])
    except MoyskladDocumentNotFoundException:
        _write_error(f'Склад "{sklad_name}" не найден!')
    except MoyskladFewDocumentsFoundException:
        _write_error(f'По названию "{sklad_name}" найдено несколько складов!')
    except MoyskladException:
        _write_error(f'Проблема с поиском склада "{sklad_name}"!')
    try:
        project = get_document(doc_type='project', filters=[f'name={project_name}'])
    except MoyskladDocumentNotFoundException:
        _write_error(f'Проект "{project_name}" не найден!')
    except MoyskladFewDocumentsFoundException:
        _write_error(f'По названию "{project_name}" найдено несколько проектов!')
    except MoyskladException:
        _write_error(f'Проблема с поиском проекта "{project_name}"!')
    try:
        product_from_table = get_document(doc_type='product', filters=[f'name={product_name}'])
    except MoyskladDocumentNotFoundException:
        _write_error(f'Товар "{product_name}" не найден!')
    except MoyskladFewDocumentsFoundException:
        _write_error(f'По названию "{product_name}" найдено несколько товаров!')
    except MoyskladException:
        _write_error(f'Проблема с поиском товара "{product_name}"!')
    try:
        report_date = datetime.strptime(date_string, '%d.%m.%Y')
    except:
        try:
            report_date = start_date + timedelta(days=date_string)
        except:
            _write_error('Укажите "Обновить на дату:" в формате "День.Месяц.Год"!')
    report = get_report_all(id=store['id'], moment=report_date)
    positions = []
    costs = []
    for id, row in enumerate(rows):
        if id >= first_string_index:
            costs.append([])
            try:
                position_debit_quantity = row[spisanie_1_column-1 + debit_num*3]
                if ',' in str(position_debit_quantity):
                    position_debit_quantity = str(position_debit_quantity).replace(',', '.')
                position_debit_quantity = float(position_debit_quantity)
                position = [pos for pos in report['rows'] if pos['name'] == row[nomenklatura_column]][0]
                if position_debit_quantity <= position['stock'] and position_debit_quantity != float(0):
                    costs[len(costs)-1] = [position.get('cost', row[sebestoimost_column])]
                    positions.append({})
                    positions[len(positions)-1]['quantity'] = position_debit_quantity
                    positions[len(positions)-1]['product'] = {'meta': position['meta']}
            except Exception as exc:
                #print(row)
                print(exc)
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet=sheet, 
        column=spisanie_1_column + debit_num*3, row_id=first_string_index+1, 
        data=costs
    )
    try:
        demand_sum = float(rows[first_string_index-4][spisanie_1_column + debit_num*3])
        if not demand_sum:
            raise
    except:
        _write_error(f'Неверно указана Сумма отгрузки по этапу! Этап №{debit_num+1}.')
    try:
        operation_date = datetime.strptime(rows[first_string_index-3][spisanie_1_column + debit_num*3], '%d.%m.%Y')
        if not operation_date:
            raise
    except:
        try:
            date = start_date + timedelta(days=rows[first_string_index-3][spisanie_1_column + debit_num*3])
        except:
            _write_error(f'Неверно указана Дата техоперации! Формат: "День.Месяц.Год". Этап №{debit_num+1}.')
    pp_body = {
        'materials': positions,
        'products': [{'product': {'meta': product_from_table['meta']}, 'quantity': demand_sum}],
        'name': f'{debit_num+1}. {sklad_name}',
    }
    try:
        pp = create_document(doc_type='processingplan', body=pp_body)
    except:
        _write_error(f'Ошибка создания тех. карты! Не указано ни одного Матреиала! (Проверьте остатки по позициям)')
    try:
        organization = get_document(doc_type='organization', filters=[f'name={organizaciya_name}'])
    except:
        _write_error(f'Ошибка! Организация "{organizaciya_name}" не найдена!')
    processing_positions = {
        "meta": {"type": "processingpositionresult"},
        'rows': []
    }
    for pos in positions:
        processing_positions['rows'].append({
            'assortment': {'meta': pos['product']['meta']}, 
            'quantity': pos['quantity']
        })
    processing_body = {
        'organization': {'meta': organization['meta']}, 
        'processingSum': 0, 'quantity': 1, 
        'processingPlan': {'meta': pp['meta']},
        'productsStore': {'meta': store['meta']},
        'materialsStore': {'meta': store['meta']},
        'materials': processing_positions,
        'products': {
            "meta": {"type": "processingpositionresult"},
            'rows': [{
                'assortment': {'meta': processed_product_meta}, 
                'quantity': demand_sum
            }]
        },
        'project': {'meta': project['meta']},
        'moment': f'''{operation_date.strftime('%Y')}-{operation_date.strftime('%m')}-{operation_date.strftime('%d')} {operation_date.strftime('%H')}:{operation_date.strftime('%M')}:{operation_date.strftime('%S')}'''
    }
    processing = create_document(doc_type='processing', body=processing_body)
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet=sheet, 
        column=spisanie_1_column + debit_num*3, row_id=first_string_index-1, 
        data=f'''=ГИПЕРССЫЛКА("{processing['meta']['uuidHref']}";"Тех. Операция в МС")'''
    )



def column_indexes(rows: list):
    """Функция находит расположение данных в таблице"""
    for id, row in enumerate(rows):
        if row.count('Номенклатура') != 0:
            global first_string_index
            first_string_index = id + 1
            global nomenklatura_column
            nomenklatura_column = row.index('Номенклатура')
            global sebestoimost_column
            sebestoimost_column = row.index('Себестоимость')
            global ostatki_column
            ostatki_column = row.index('Остатки текущие')
            global spisanie_1_column
            spisanie_1_column = row.index('Списание Этап №1') + 1
            break
    for id, row in enumerate(rows):
        if row.count('Номенклатура техкарты:') != 0:
            global product_name
            product_name = row[row.index('Номенклатура техкарты:') + 1]
            break
    for id, row in enumerate(rows):
        if row.count('Обновить на дату:') != 0:
            global date_string
            date_string = row[row.index('Обновить на дату:') + 1]
            break
    for id, row in enumerate(rows):
        if row.count('Склад:') != 0:
            global sklad_name
            sklad_name = row[row.index('Склад:') + 1]
            break
    for id, row in enumerate(rows):
        if row.count('Проект:') != 0:
            global project_name
            project_name = row[row.index('Проект:') + 1]
            break
    for id, row in enumerate(rows):
        if row.count('Организация:') != 0:
            global organizaciya_name
            organizaciya_name = row[row.index('Организация:') + 1]
            break
    for id, row in enumerate(rows):
        if row.count('Результат работы прогр.:') != 0:
            global result_row
            result_row = id + 1
            global result_column
            result_column = row.index('Результат работы прогр.:') + 1
            break

def _write_error(text, raise_exception=True):
    now = datetime.now()
    if text:
        text += f' ({now.strftime("%d")}.{now.strftime("%m")}.{now.strftime("%Y")} {now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")})'
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet=sheet, column=spisanie_1_column + debit_num*3, 
        row_id=first_string_index-4, data=text
    )
    if raise_exception:
        raise











