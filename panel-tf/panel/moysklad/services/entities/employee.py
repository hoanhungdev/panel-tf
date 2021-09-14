from moysklad.services.entities.base import get_documents

def get_employees_name_with_attribute_value(attribute_name: str):
    emps_box_office = []
    emps = get_documents(doc_type='employee')
    for emp in emps:
        attrs = emp.get('attributes', [])
        for attr in attrs:
            if attribute_name.lower() in attr['name'].lower():
                emps_box_office.append({})
                emps_box_office[len(emps_box_office) - 1]['name'] = emp['name']
                emps_box_office[len(emps_box_office) - 1]['attribute_value'] = attr['value']
                emps_box_office[len(emps_box_office) - 1]['entity_type'] = emp['meta']['type'] # employee - тип этого документа
                emps_box_office[len(emps_box_office) - 1]['entity_id'] = emp['id']
    return emps_box_office

def get_employees_name_and_meta():
    employees = get_documents(doc_type='employee')
    return [{'name': emp['shortFio'], 'meta': emp['meta']} for emp in employees]
