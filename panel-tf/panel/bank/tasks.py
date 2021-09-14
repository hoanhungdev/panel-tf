from panel.celery import app
from .services.bank_statement import get_bank_statement




@app.task
def get_bank_statement_celery_task():
    get_bank_statement()
