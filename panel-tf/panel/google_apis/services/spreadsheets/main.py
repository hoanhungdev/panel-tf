from typing import Union
from decimal import Decimal
from datetime import datetime, timedelta

import apiclient.discovery
from google_apis.services.base import httpAuth, developerKey

from google_apis.services.base import base_sheets_date

# Английский алфавит
alphabet = []
for number in range(65, 91):
    alphabet.append(chr(number))
for number1 in range(65, 91):
    for number2 in range(65, 91):
        alphabet.append(f'{chr(number1)}{chr(number2)}')
start_date = datetime(day=30, month=12, year=1899)

def _get_spreadsheets_service():
    return apiclient.discovery.build("sheets", "v4",
                    http = httpAuth,
                    developerKey=developerKey)

def convert_sheets_date_to_datetime(date: int):
    return base_sheets_date + timedelta(days=date)

def delete_rows(
        spreadsheet_id: str, sheet_id: int, start_index: int, end_index: int
    ):
    service = _get_spreadsheets_service()
    body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": start_index,
                        "endIndex": end_index
                    }
                }
            }
        ],
    }
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    return result
    

def get_table(spreadsheet_id: str, sheet: str):
    service = _get_spreadsheets_service()
    data = service.spreadsheets().get(spreadsheetId=spreadsheet_id,
        ranges=f"{sheet}!1:1",
        includeGridData=True).execute()
    return data

def get_table_name(spreadsheet_id: str, sheet: str):
    table_name = get_table(spreadsheet_id, sheet)["properties"]["title"]
    return table_name

def get_sheet_id(spreadsheet_id: str, sheet: str):
    sheets = get_table(spreadsheet_id, sheet)["sheets"]
    sheets = [s['properties']['sheetId'] for s in sheets if s['properties']['title'] == sheet]
    if not sheets:
        raise
    return sheets[0]

def get_spreadsheet_rows(spreadsheet_id: str, sheet: str, 
        value_render_option='FORMATTED_VALUE'):
    service = _get_spreadsheets_service()
    data = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet}!A1:ZZZ1000", majorDimension="ROWS", 
        valueRenderOption=value_render_option
    ).execute()
    return data.get("values", [])
    
def write_to_sheet(
        spreadsheet_id: str, sheet: str, column: Union[str, int, type(Decimal())], row_id: int,
        data: Union[list, str, int]
    ):
    try:
        column = alphabet[int(column)]
    except ValueError:
        pass # значит колонна задана уже буквой
    if type(data) in [str, int, float]:
        if '=' in str(data):
            return write_link(spreadsheet_id, sheet, alphabet.index(column), row_id, data)
        data = [[data]]
    elif type(data) == list:
        try:
            if type(data[0]) != list:
                data = [data]
        except:
            pass
    elif type(data) == type(Decimal()):
        data = [[str(data).replace('.', ',')]]
    service = _get_spreadsheets_service()
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": f"{sheet}!{column}{row_id}",
            "values": data}
        ]
    }
    result = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
        body=body).execute()
    return result

def write_link(
        spreadsheet_id: str, sheet: str, column: int, row_id: int,
        data: str
    ):
    requests = []
    sheet_id = get_sheet_id(spreadsheet_id=spreadsheet_id, sheet=sheet)
    requests.append({
        "updateCells": {
            "rows": [
                {
                    "values": [{
                        "userEnteredValue": {
                            "formulaValue": data
                        }
                    }]
                }
            ],
            "fields": "userEnteredValue",
            "start": {
                "sheetId": sheet_id,
                "rowIndex": row_id-1,
                "columnIndex": column
            }
        }})
    body = {
        "requests": requests
    }
    service = _get_spreadsheets_service()
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body)
    return request.execute()

def clear_sheet_range(spreadsheet_id: str, sheet: str, start: str, finish: str):
    service = _get_spreadsheets_service()
    result = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id,
        range=f'{sheet}!{start}:{finish}'
    ).execute()
    return result

def batch_update(spreadsheet_id: str, data):
    service = _get_spreadsheets_service()
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=data
    ).execute()
    return result

def copy_to(from_spreadsheet_id: str, to_spreadsheet_id: id, from_sheet_id: int):
    body = {
      "destinationSpreadsheetId": to_spreadsheet_id
    }
    service = _get_spreadsheets_service()
    result = service.spreadsheets().sheets().copyTo(
        spreadsheetId=from_spreadsheet_id, sheetId=from_sheet_id, 
        body=body
    ).execute()
    return result

def add_rows(spreadsheet_id: str, range: str, data):
    service = _get_spreadsheets_service()
    body = {
        'values': data
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range, 
        valueInputOption='USER_ENTERED', body=body,
        insertDataOption='INSERT_ROWS'
    ).execute()
    return result










