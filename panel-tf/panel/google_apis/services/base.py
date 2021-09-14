import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from datetime import datetime

CREDENTIALS_FILE = '../keys/google.json'  # имя файла с закрытым ключом

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
developerKey = "AIzaSyCjk9er5Ip0mhd4DJnnLFlI8sLr8QwX8Qk"

# апи отдаёт дату в виде количества дней, которые надо прибавить к следующей дате:
base_sheets_date = datetime(day=30, month=12, year=1899)



