from panel.celery import app
from create_project_folder.services.main import create_project_folder_by_webhook, \
    create_project_folder_by_spreadsheet_link


@app.task
def create_project_folder_by_webhook_task(deal_id):
    create_project_folder_by_webhook(deal_id=deal_id)

@app.task
def create_project_folder_by_spreadsheet_link_task():
    create_project_folder_by_spreadsheet_link()

