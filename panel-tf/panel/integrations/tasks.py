from panel.celery import app
from integrations.services.bitrix import add_utms

@app.task
def add_utms_task(utms_id: int):
    add_utms(utms_id=utms_id)
