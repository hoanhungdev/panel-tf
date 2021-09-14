from datetime import datetime, timedelta
from moysklad.services.entities.base import get_documents
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range
from info_lists.services.base import spreadsheet_id

def _write(row: int, col: str, data):
    write_to_sheet(
        spreadsheet_id=spreadsheet_id, sheet='Проекты', column=col, 
        row_id=row, data=data
    )

def _clear(start: str, finish: str):
    clear_sheet_range(
        spreadsheet_id=spreadsheet_id, sheet='Проекты', start=start, 
        finish=finish
    )



def load_projects():
    project_close_option_id = '03ecc5ba-62bf-11e8-9109-f8fc00000eca'
    project_rp_attr_id = '46152295-62be-11e8-9109-f8fc00001531'
    projects = get_documents(doc_type='project')

    
    #фильтр по аттрибуту "ПроектЗакрыт" закомментирован
    project_names = []

    for id, project in enumerate(projects):
        #ClosedAttrExists = False
        rp = ''
        try:
            for attr in project['attributes']:
                if attr['id'] == project_rp_attr_id:
                    rp = attr['value']['name']
        except:
            rp = ''
        project_names.append([project['name'], rp])
        #try:
        #    for attr in project['attributes']:
        #        if attr['meta'] == project_close_option_meta:
        #            if attr['value'] == False:
        #                project_names.append([project['name'], rp])
        #                break
        #            ClosedAttrExists = True
        #        else:
        #            pass
        #except KeyError:
        #    project_names.append([project['name'], rp])
        #try: # добавляю те проекты, где нет "Проект закрыт" в аттрибутах
        #    if (project_names[-1][0] != project['name']) and (ClosedAttrExists == False):
        #        project_names.append([project['name'], rp])
        #except:
        #    pass


    ######################################################################
    now = datetime.now()
    header = [
        ["Проекты"], 
        ["Обновлено {}.{}.{} в {}:{}:{}".format(now.strftime("%d"), now.strftime("%m"), now.strftime("%Y"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"))],
        ['Проект закрыт: Нет'], [], [], ['Проект', 'РП']
    ]
    table = [*header, *project_names]
    
    _clear(start='A1', finish='C1000')
    _write(row=1, col=0, data=table)































