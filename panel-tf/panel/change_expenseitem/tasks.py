from panel.celery import app
from change_expenseitem.services.main import start

@app.task
def start_task():
    start()


