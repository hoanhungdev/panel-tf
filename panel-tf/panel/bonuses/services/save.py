#from loguru import logger
from datetime import datetime
from decimal import Decimal

from moysklad.services.entities.base import get_documents, get_document_by_id
from bonuses.services.base import spreadsheet_id, b1_sheet_id, summary_sheet_id, \
    get_sheet_name_from_spreadsheets, summary_sheet_id, summary_sheet_name
from summary_table.services.base import reestr_proektov_customerorder_state, search_attr_value_by_id, add, format_sum, \
    format_date, format_bool, format_double, chained_get, get_sum_by_doc_type
from google_apis.services.spreadsheets.main import write_to_sheet, \
    copy_to, batch_update, get_spreadsheet_rows

#logger.add(
#    '/home/admin/code/panel-tf/panel/summary_table/logs/debug.log', 
#    format="{time} {level} {message}", level='DEBUG', rotation='1 week', 
#    compression='zip', retention="49 days"
#)



def save_bonuses():
    sheet = get_sheet_name_from_spreadsheets()
    start(sheet)

def start(sheet: str):
    global now
    global table
    table = []
    now = datetime.now()
    # создаю новый лист
    new_sheet = copy_to(
        from_spreadsheet_id=spreadsheet_id, from_sheet_id=summary_sheet_id,
        to_spreadsheet_id=spreadsheet_id
    )
    # получаю значения
    table = get_spreadsheet_rows(
        spreadsheet_id=spreadsheet_id, 
        sheet=summary_sheet_name
    )
    body = {
        "requests": [{
            "updateSheetProperties": {
                "properties": {
                    "sheetId": new_sheet['sheetId'],
                    "title": sheet,
                },
                "fields": "title",
            }
        }]
    }
    # меняю имя листа
    batch_update(spreadsheet_id=spreadsheet_id, data=body)
    # записываю значения
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet=sheet, column=0, row_id=1, 
        data=table
    )
    
    















