from panel.celery import app
from processingplan.services.main import start

@app.task
def start_task():
    start()


