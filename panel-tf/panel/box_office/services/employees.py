from datetime import datetime
from moysklad.services.entities.organization import \
        get_organizations_name_with_attribute_value
from moysklad.services.entities.employee import \
    get_employees_name_with_attribute_value
from google_apis.services.spreadsheets.main import get_spreadsheet_rows, \
    write_to_sheet, clear_sheet_range


def load_payments():
    orgs_box_office = get_organizations_name_with_attribute_value(attribute_name='Касса')
    if len(orgs_box_office) > 1 or len(orgs_box_office) < 1 or \
            not orgs_box_office[0]['attribute_value'].startswith('https://docs.google.com/spreadsheets/d/'):
        raise Exception
    org_spreadsheet_id = orgs_box_office[0]['attribute_value'][39:83]
    rows = []
    box_office = get_employees_name_with_attribute_value(attribute_name="Касса")
    box_office = [bo for bo in box_office \
        if bo['attribute_value'].startswith('https://docs.google.com/spreadsheets/d/')]
    for bo in box_office:
        bo_rows = get_spreadsheet_rows(
            spreadsheet_id=bo['attribute_value'][39:83],
            sheet='РАЗБОР',
            value_render_option='FORMULA'
        )[5:]
        rows += [[bo['name']] + row for row in bo_rows]
    print(rows)
    rows = [row for row in rows if len(row) > 2]
    print(rows)
    filtered_rows = []
    for row in rows:
        try:
            if type(row[1]) == int:
                if row[1] != 0:
                    filtered_rows.append(row)
            elif type(row[2]) == int:
                if row[2] != 0:
                    filtered_rows.append(row)
            elif row[1].replace(' ', '') != '' or row[2].replace(' ', '') != '':
                filtered_rows.append(row)
        except:
            pass
    now = datetime.now()
    clear_sheet_range(spreadsheet_id=org_spreadsheet_id, 
        sheet='СОТРУДНИКИ', start='A6', finish='N10000')
    _write(spreadsheet_id=org_spreadsheet_id, 
        data=f"Обновлено: {now.strftime('%d')}.{now.strftime('%m')}.{now.strftime('%Y')} {now.strftime('%H')}:{now.strftime('%M')}", row_id=1)
    _write(spreadsheet_id=org_spreadsheet_id, data=filtered_rows, row_id=6)
    
    
    
    
def _write(spreadsheet_id, data, row_id):
    write_to_sheet(spreadsheet_id=spreadsheet_id,
        sheet='СОТРУДНИКИ', column=0, row_id=row_id, data=data)












