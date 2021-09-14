from panel.celery import app
from stock_report.services.main import update_table, check_archive, save_table


@app.task
def update_table_task():
    update_table()
    
@app.task
def save_table_task():
    save_table()


@app.task
def check_archive_task():
    check_archive()
