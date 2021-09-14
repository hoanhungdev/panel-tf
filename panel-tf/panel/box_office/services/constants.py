ao_customentity_id = '0db49c3a-b208-11e6-7a69-8f55000132ce'
report_document_sheet_id = 86796709


def get_body_for_write_report(doc_type: str):
    if doc_type == 'cashin':
        id = '9b88ebf1-b208-11e6-7a31-d0fd0001b822'
    elif doc_type == 'cashout':
        id = '311d7d49-b208-11e6-7a31-d0fd0001b08d'
    return {
    "attributes" : [ {
        "meta" : {
            "href" : f"https://online.moysklad.ru/api/remap/1.2/entity/{doc_type}/metadata/attributes/{id}",
            "type" : "attributemetadata",
            "mediaType" : "application/json"
        },
        "value": {
            "meta": 'новый ао' # подстановка
        }
    }]
}
ao_meta = { # авансовый отчет "0"
    "href": "https://online.moysklad.ru/api/remap/1.2/entity/customentity/0db49c3a-b208-11e6-7a69-8f55000132ce/27881a35-b348-11e6-7a69-8f5500289c2d",
    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/companysettings/metadata/customEntities/0db49c3a-b208-11e6-7a69-8f55000132ce",
    "type": "customentity",
    "mediaType": "application/json",
    "uuidHref": "https://online.moysklad.ru/app/#custom_0db49c3a-b208-11e6-7a69-8f55000132ce/edit?id=27881a35-b348-11e6-7a69-8f5500289c2d"
}
organization_meta = { # Техно Фасад
    "href": "https://online.moysklad.ru/api/remap/1.2/entity/organization/b66837ad-d66c-11e6-7a69-9711004b5836",
    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/organization/metadata",
    "type": "organization",
    "mediaType": "application/json",
    "uuidHref": "https://online.moysklad.ru/app/#mycompany/edit?id=b66837ad-d66c-11e6-7a69-9711004b5836"
}
project_for_cashout = { # проект "Перемещение ДС"
    "href" : "https://online.moysklad.ru/api/remap/1.2/entity/project/88afe399-49f6-11ea-0a80-051a000bdb54",
    "metadataHref" : "https://online.moysklad.ru/api/remap/1.2/entity/project/metadata",
    "type" : "project",
    "mediaType" : "application/json"
}
expenseitem_for_cashout =  { # статья расхода "ПЕРЕМЕЩЕНИЕ"
    "href" : "https://online.moysklad.ru/api/remap/1.2/entity/expenseitem/4e50ea24-0673-11e6-97e5-0cc47a342c9e",
    "metadataHref" : "https://online.moysklad.ru/api/remap/1.2/entity/expenseitem/metadata",
    "type" : "expenseitem",
    "mediaType" : "application/json"
}
body_cashout = {
    "organization": {"meta": organization_meta}, # подстановка
    "agent": {"meta": "counterparty_meta"}, # подстановка
    "sum": "amount", # подстановка
    "attributes": [{
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/cashout/metadata/attributes/311d7d49-b208-11e6-7a31-d0fd0001b08d",
            "type": "attributemetadata",
            "mediaType": "application/json"
        },
        "id": "311d7d49-b208-11e6-7a31-d0fd0001b08d",
        "name": "Авансовый отчет",
        "type": "customentity",
        "value": {
            "meta": "ao_meta" # подстановка
        }
    }],
    "description": "comment", # подстановка
    "applicable": True,
    "operations": [{"meta": "customerorder_meta", "linkedSum": "amount"}], # подстановка
    "expenseItem": {"meta": expenseitem_for_cashout}, # подстановка
    "project": {"meta": project_for_cashout} # подстановка
}
body_cashin = {
    "organization": {"meta": organization_meta}, # подстановка
    "agent": {"meta": "counterparty_meta"}, # подстановка
    "sum": "amount", # подстановка
    "attributes": [{
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/cashin/metadata/attributes/9b88ebf1-b208-11e6-7a31-d0fd0001b822",
            "type": "attributemetadata",
            "mediaType": "application/json"
        },
        "customEntityMeta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/companysettings/metadata/customEntities/0db49c3a-b208-11e6-7a69-8f55000132ce",
            "type": "customentitymetadata",
            "mediaType": "application/json"
        },
        "id": "9b88ebf1-b208-11e6-7a31-d0fd0001b822",
        "name": "Авансовый отчет",
        "type": "customentity",
        "value": {
            "meta": "ao_meta" # подстановка
        }
    }],
    "description": "comment", # подстановка
    "applicable": True,
    "operations": [{"meta": "customerorder_meta", "linkedSum": "amount"}], # подстановка
    "project": {"meta": "project_meta"} # подстановка
}

default_expenseitem = {'meta': {
    "href" : "https://online.moysklad.ru/api/remap/1.2/entity/expenseitem/5582edc6-0a01-11e4-8149-0cc47a02273e",
    "metadataHref" : "https://online.moysklad.ru/api/remap/1.2/entity/expenseitem/metadata",
    "type" : "expenseitem",
    "mediaType" : "application/json"
}}