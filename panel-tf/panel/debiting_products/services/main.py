from datetime import datetime, timedelta

from google_apis.services.spreadsheets.main import \
        get_spreadsheet_rows, write_to_sheet, start_date
from moysklad.services.reports.stock import get_report_all
from moysklad.services.entities.base import get_document
from moysklad.services.base import MoyskladException, \
    MoyskladDocumentNotFoundException, MoyskladFewDocumentsFoundException

from .base import sheet

def update_table(ss_id: str):
    global spreadsheet_id
    spreadsheet_id = ss_id
    rows = get_spreadsheet_rows(
        spreadsheet_id=spreadsheet_id, 
        sheet=sheet, 
        value_render_option='UNFORMATTED_VALUE'
    )
    column_indexes(rows)
    for id, row in enumerate(rows):
        rows[id] = rows[id][:ostatki_column]
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
        report_date = datetime.strptime(date_string, '%d.%m.%Y')
    except:
        try:
            report_date = start_date + timedelta(days=date_string)
        except:
            _write_error('Укажите "Обновить на дату:" в формате "День.Месяц.Год"!')
    report = get_report_all(id=store['id'], moment=report_date)
    for id, row in enumerate(rows):
        if id >= first_string_index:
            product = [{'id': id, 'name': p['name'], 'uom': p['uom']['name'], 'cost': format_ms_number(p['price']), 'stock': p['stock']} for p in report['rows'] if row[nomenklatura_column] == p['name']]
            if  len(product) > 1:
                _write_error(f'''По номенклатуре "{row['nomenklatura_column']}" найдено несколько товаров!''')
            elif len(product) == 0:
                try:
                    rows[id][sebestoimost_column] = 0
                except:
                    rows[id].append(0)
                try:
                    rows[id][ostatki_column] = 0
                except:
                    rows[id].append(0)
            elif len(product) == 1:
                print(row[nomenklatura_column])
                print(product[0].get('stock', 0))
                try:
                    rows[id][sebestoimost_column] = product[0].get('cost', 0)
                except:
                    rows[id].append(product[0].get('cost', 0))
                try:
                    rows[id][ostatki_column] = product[0].get('stock', 0)
                except:
                    rows[id].append(product[0].get('stock', 0))
    add_rows = []
    for id, product in enumerate(report['rows']):
        row = [r for r in rows[first_string_index:] if product['name'] == r[nomenklatura_column]]
        if len(row) > 1:
            _write_error(f'''По номенклатуре "{product['name']}" найдено несколько товаров!''')
        elif len(row) == 0:
            add_rows += [[product['folder']['pathName'], product['name'], product['uom']['name'], format_ms_number(product['price']), product['stock']]]
    rows += add_rows
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet=sheet, column=0, 
        row_id=first_string_index + 1, data=rows[first_string_index:]
    )
    _write_error('Данные успешно обновлены!')
    

def format_ms_number(number):
    number = round(number)
    return float(f'{number//100}.{number%100}')

def column_indexes(rows: list):
    """Функция находит расположение данных в таблице"""
    for id, row in enumerate(rows):
        if row.count('Номенклатура') != 0:
            global first_string_index
            first_string_index = id + 1
            global nomenklatura_column
            nomenklatura_column = row.index('Номенклатура')
            global ed_ism_column
            ed_ism_column = row.index('Ед изм')
            global sebestoimost_column
            sebestoimost_column = row.index('Себестоимость')
            global ostatki_column
            ostatki_column = row.index('Остатки текущие')
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
        if row.count('Результат работы прогр.:') != 0:
            global result_row
            result_row = id + 1
            global result_column
            result_column = row.index('Результат работы прогр.:') + 1
            break

def _write_error(text):
    now = datetime.now()
    text += f' ({now.strftime("%d")}.{now.strftime("%m")}.{now.strftime("%Y")} {now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")})'
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet=sheet, column=result_column, 
        row_id=result_row, data=text
    )
    if 'успешно' not in text.lower():
        raise











