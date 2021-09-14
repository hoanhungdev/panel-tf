from datetime import datetime
from moysklad.services.entities.base import get_documents
from moysklad.services.reports.stock import get_report_by_store, \
    get_report_all
from google_apis.services.spreadsheets.main import write_to_sheet, \
    clear_sheet_range, copy_to, batch_update, get_spreadsheet_rows

from .base import spreadsheet_id, report_sheet, report_sheet_id, archive_sheet



def update_table():
    stores = get_documents(doc_type='store', filters=['archived=false'])
    reports = []
    tree = {}
    project_stores = []
    for store in stores:
        report = get_report_all(id=store['id'], filters=['archived=false'])['rows']
        prices = [rep['price'] * rep['quantity'] for rep in report]
        sum_prices = int(sum(prices))
        price = float(f'{sum_prices // 100}.{sum_prices % 100}')
        store_data = {
            'name': store['name'], 
            'sum': price,
            'report_link': f"https://online.moysklad.ru/app/#stockReport?reportType=GOODS&global_archivedFilter=All&storeIdFilter=[{store['id']}\\,{store['name']}\\,\\,Warehouse],equals"
        }
        path = store['pathName'].split('/')
        if path == ['']:
            path.pop(0)
        if not store['pathName']:
            tree = place_store_data(tree, path, store_data)
        else:
            tree = add_keys_to_tree(tree, path, store_data)
            tree = place_store_data(tree, path, store_data)
            
    for item in tree.items():
        if item[0] == 'values':
            for value in item[1]:
                project_stores = add_row(project_stores=project_stores, store_data=value)
        else:
            project_stores = prettify_stores(project_stores, item[1])
            
    #for pr in project_stores:
    #    print(pr)
    now = datetime.now()
    header = [
        ['Остатки на складах'], 
        [f'Обновлено ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} в ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")}']
    ]
    project_stores = header + [[''], [''], [''], [''], ['Склад', '', '', '', '', 'Сумма']] + project_stores
    clear_sheet_range(spreadsheet_id=spreadsheet_id, sheet=report_sheet, start='A1', finish='Z1000')
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet=report_sheet, column=0, row_id=1, data=project_stores)

def prettify_stores(project_stores, root_branch):
    values = root_branch.get('values', [])
    values.sort(key=lambda item: item['name'])
    for value in values:
        project_stores = add_row(project_stores, value)
        branch = root_branch.get(value['name'])
        if branch:
            values1 = branch.get('values', [])
            values1.sort(key=lambda item: item['name'])
            for value1 in values1:
                project_stores = add_row(project_stores, value1, empty_cells=1)
                branch1 = root_branch[value['name']].get(value1['name'])
                if branch1:
                    values2 = branch1.get('values', [])
                    values2.sort(key=lambda item: item['name'])
                    for value2 in values2:
                        project_stores = add_row(project_stores, value2, empty_cells=2)
                        branch2 = root_branch[value['name']][value1['name']].get(value2['name'])
                        if branch2:
                            values3 = branch2.get('values', [])
                            values3.sort(key=lambda item: item['name'])
                            for value3 in values3:
                                project_stores = add_row(project_stores, value3, empty_cells=3)
                                branch2 = root_branch[value['name']][value1['name']][value2['name']].get(value3['name'])
    return project_stores

def add_row(project_stores, store_data, empty_cells=0):
    project_stores.append([])
    for i in range(empty_cells):
        project_stores[-1].append('')
    name = f"""=ГИПЕРССЫЛКА("{store_data['report_link']}";"{store_data['name']}")"""
    project_stores[-1].append(name)
    while(len(project_stores[-1]) < 5):
        project_stores[-1].append('')
    project_stores[-1].append(store_data['sum'])
    return project_stores

def add_keys_to_tree(tree, path, store_data):
    len_path = len(path)
    if len_path >= 1:
        item = tree.get(path[0], {})
        if not item:
            tree[path[0]] = {}
        else:
            tree[path[0]] = item
    if len_path >= 2:
        item = tree[path[0]].get(path[1], {})
        if not item:
            tree[path[0]][path[1]] = {}
        else:
            tree[path[0]][path[1]] = item
    if len_path >= 3:
        item = tree[path[0]][path[1]].get(path[2], {})
        if not item:
            tree[path[0]][path[1]][path[2]] = {}
        else:
            tree[path[0]][path[1]][path[2]] = item
    if len_path >= 4:
        item = tree[path[0]][path[1]][path[2]].get(path[3], {})
        if not item:
            tree[path[0]][path[1]][path[2]][path[3]] = {}
        else:
            tree[path[0]][path[1]][path[2]][path[3]] = item
    return tree

def place_store_data(tree, path, store_data):
    len_path = len(path)
    if len_path == 0:
        if tree.get('values'):
            tree['values'].append(store_data)
        else:
            tree['values'] = [store_data]
    if len_path == 1:
        if tree[path[0]].get('values'):
            tree[path[0]]['values'].append(store_data)
        else:
            tree[path[0]]['values'] = [store_data]
    if len_path == 2:
        if tree[path[0]][path[1]].get('values'):
            tree[path[0]][path[1]]['values'].append(store_data)
        else:
            tree[path[0]][path[1]]['values'] = [store_data]
    if len_path == 3:
        if tree[path[0]][path[1]][path[2]].get('values'):
            tree[path[0]][path[1]][path[2]]['values'].append(store_data)
        else:
            tree[path[0]][path[1]][path[2]]['values'] = [store_data]
    if len_path == 4:
        if tree[path[0]][path[1]][path[2]][path[3]].get('values'):
            tree[path[0]][path[1]][path[2]][path[3]]['values'].append(store_data)
        else:
            tree[path[0]][path[1]][path[2]][path[3]]['values'] = [store_data]
    return tree

def check_archive():
    stores = get_documents(doc_type='store', filters=['archived=true'])
    reports = []
    tree = {}
    project_stores = []
    for store in stores:
        report = get_report_all(id=store['id'], filters=['archived=false'])['rows']
        prices = [rep['price'] * rep['quantity'] for rep in report]
        sum_prices = int(sum(prices))
        price = float(f'{sum_prices // 100}.{sum_prices % 100}')
        if price == float(0):
            continue
        store_data = {
            'name': store['name'], 
            'sum': price,
            'report_link': f"https://online.moysklad.ru/app/#stockReport?reportType=GOODS&global_archivedFilter=All&storeIdFilter=[{store['id']}\\,{store['name']}\\,\\,Warehouse],equals"
        }
        path = store['pathName'].split('/')
        if path == ['']:
            path.pop(0)
        if not store['pathName']:
            tree = place_store_data(tree, path, store_data)
        else:
            tree = add_keys_to_tree(tree, path, store_data)
            tree = place_store_data(tree, path, store_data)
            
    for item in tree.items():
        if item[0] == 'values':
            for value in item[1]:
                project_stores = add_row(project_stores=project_stores, store_data=value)
        else:
            project_stores = prettify_stores(project_stores, item[1])
            
    #for pr in project_stores:
    #    print(pr)
    now = datetime.now()
    header = [
        ['Остатки на Архивных складах'], 
        [f'Обновлено ' \
        f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year} в ' \
        f'{now.strftime("%H")}:{now.strftime("%M")}:{now.strftime("%S")}']
    ]
    project_stores = header + [[''], [''], [''], [''], ['Склад', '', '', '', '', 'Сумма']] + project_stores
    clear_sheet_range(spreadsheet_id=spreadsheet_id, sheet=archive_sheet, start='A1', finish='Z1000')
    write_to_sheet(spreadsheet_id=spreadsheet_id, sheet=archive_sheet, column=0, row_id=1, data=project_stores)

def save_table():
    table = []
    now = datetime.now()
    # создаю новый лист с теми же данными
    new_sheet = copy_to(
        from_spreadsheet_id=spreadsheet_id, from_sheet_id=report_sheet_id,
        to_spreadsheet_id=spreadsheet_id
    )
    body = {
        "requests": [{
            "updateSheetProperties": {
                "properties": {
                    "sheetId": new_sheet['sheetId'],
                    "title": f'{now.strftime("%d")}.{now.strftime("%m")}.{now.year}',
                },
                "fields": "title",
            }
        }]
    }
    # меняю имя листа
    batch_update(spreadsheet_id=spreadsheet_id, data=body)



