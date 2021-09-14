from panel.celery import app
from start_project.services.main import start_project_by_webhook, \
    start_project_by_spreadsheet_link



@app.task(bind=True)
def start_project_by_webhook_task(self, deal_id: str):
    start_project_by_webhook(deal_id=deal_id)

@app.task
def start_project_by_spreadsheet_link_task():
    start_project_by_spreadsheet_link()










