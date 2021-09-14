from moysklad.services.entities.base import get_documents






def _get_productfolders():
    rows = get_documents(doc_type='productfolder', filters=['archived=false'])
    rows = [row for row in rows if row['name'] != 'Корневая группа']
    for id, pf in enumerate(rows):
        pathName = pf.get('pathName', '').split('/')
        pathName.pop(pathName.index('Корневая группа'))
        rows[id]['pathName'] = pathName
    return rows










