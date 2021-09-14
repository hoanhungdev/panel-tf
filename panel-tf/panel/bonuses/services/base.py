from datetime import datetime
from google_apis.services.spreadsheets.main import get_spreadsheet_rows, \
    write_to_sheet



spreadsheet_id = '1OiJPeQ0kvXUi_fZkbBeT4MJLnKdb32GuOoNVwQznk38'
#spreadsheet_id = '1NcEmaLipv03SinwIkcVtGcegMGWYs_-G5ldTvR_CnIE'
control_spreadsheet_id = '1St0oJJIKf3xUhrjDv9sZG5aH6V-2Rbqidj4lR5WHqNw'
control_sheet = 'Функции'
b1_sheet_id = 1171823070
b2_sheet_id = 371910542
summary_sheet_id = 59977636
summary_sheet_name = 'Сводная таблица бонусов'

def get_dates_from_spreadsheets():
    flag = False
    rows = get_spreadsheet_rows(
        spreadsheet_id=spreadsheet_id, 
        sheet=summary_sheet_name
    )
    errors_col_num = False
    for row_id, row in enumerate(rows):
        for col_id, item in enumerate(row):
            
            if item == 'Бонусы':
                flag = True
            if item == 'Дата с' and flag:
                date_from_row_num = row_id + 1
                date_from_col_num = col_id
            if item == 'Дата по' and flag:
                date_to_row_num = row_id + 1
                date_to_col_num = col_id
            if item == 'Результаты' and flag:
                errors_col_num = col_id
                break
        if errors_col_num:
            break
    try:
        date_from = datetime.strptime(
            rows[date_from_row_num][date_from_col_num], 
            '%d.%m.%Y'
        )
        date_to = datetime.strptime(
            rows[date_to_row_num][date_to_col_num], 
            '%d.%m.%Y'
        )
        write_to_sheet(
            spreadsheet_id=spreadsheet_id,
            sheet=summary_sheet_name,
            column=errors_col_num, row_id=date_to_row_num+1,
            data=''
        )
        return {'date_from': date_from, 'date_to': date_to}
    except:
        write_to_sheet(
            spreadsheet_id=spreadsheet_id,
            sheet=summary_sheet_name,
            column=errors_col_num, row_id=date_to_row_num+1,
            data=f'Ошибка: невозможно получить входные данные!'
        )

def get_sheet_name_from_spreadsheets():
    flag = False
    rows = get_spreadsheet_rows(
        spreadsheet_id=control_spreadsheet_id, 
        sheet=control_sheet
    )
    sheet_name_col_num = False
    for row_id, row in enumerate(rows):
        for col_id, item in enumerate(row):
            if item == 'Результаты':
                errors_col_num = col_id
            if item == 'Бонусы':
                flag = True
            if item == 'Название вкладки' and flag:
                sheet_name_row_num = row_id + 1
                sheet_name_col_num = col_id
                break
        if sheet_name_col_num:
            break
    sheet = rows[sheet_name_row_num][sheet_name_col_num]
    if not sheet:
        raise
    try:
        get_spreadsheet_rows(
            spreadsheet_id=control_spreadsheet_id, 
            sheet=sheet
        )
        write_to_sheet(
            spreadsheet_id=control_spreadsheet_id,
            sheet=control_sheet,
            column=errors_col_num, row_id=sheet_name_row_num,
            data=f'Ошибка: не задано имя листа или лист с таким именем уже существует!'
        )
    except:
        write_to_sheet(
            spreadsheet_id=control_spreadsheet_id,
            sheet=control_sheet,
            column=errors_col_num, row_id=sheet_name_row_num,
            data=f''
        )
        return sheet
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
