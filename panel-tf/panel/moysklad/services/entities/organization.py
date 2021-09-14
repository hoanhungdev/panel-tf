from moysklad.services.entities.base import get_documents

def get_organizations_name_with_attribute_value(attribute_name: str):
    orgs_box_office = []
    orgs = get_documents(doc_type='organization')
    for org in orgs:
        attrs = org.get('attributes', [])
        for attr in attrs:
            if attribute_name.lower() in attr['name'].lower():
                orgs_box_office.append({})
                orgs_box_office[len(orgs_box_office) - 1]['name'] = org['name']
                orgs_box_office[len(orgs_box_office) - 1]['attribute_value'] = attr['value']
                orgs_box_office[len(orgs_box_office) - 1]['entity_type'] = org['meta']['type'] # organization - тип этого документа
                orgs_box_office[len(orgs_box_office) - 1]['entity_id'] = org['id']
    return orgs_box_office
