from panel.celery import app
from .services.main import proceed_single, proceed_all
from .services.employees import load_payments
from box_office.services.create_report import proceed_all_box_office as create_report_for_all_box_office



@app.task
def proceed_single_box_office(bo_link):
    proceed_single(bo_link)

@app.task
def proceed_all_box_office():
    proceed_all()

@app.task
def load_employees_payments_task():
    load_payments()

@app.task
def create_report_for_all():
    create_report_for_all_box_office()
