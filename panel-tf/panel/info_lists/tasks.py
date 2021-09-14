from panel.celery import app
from .services.counterparties import load_counterparties
from .services.projects import load_projects
from .services.expenseitems import load_expenseitems
from .services.stores import load_stores, load_stores_by_webhook
from .services.product_folders import load_product_folders, load_product_folders_by_webhook
from .services.employees import load_employees, load_employees_by_webhook




@app.task
def load_counterparties_celery():
    load_counterparties()

@app.task
def load_projects_celery():
    load_projects()
    
@app.task
def load_expenseitems_celery():
    load_expenseitems()    
    
@app.task
def load_stores_task():
    load_stores()
    
@app.task
def load_stores_by_webhook_task():
    load_stores_by_webhook()
    
@app.task
def load_product_folders_task():
    load_product_folders()
    
@app.task
def load_product_folders_by_webhook_task():
    load_product_folders_by_webhook()
    
@app.task
def load_employees_task():
    load_employees()
    
@app.task
def load_employees_by_webhook_task():
    load_employees_by_webhook()
