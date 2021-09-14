from panel.celery import app
from bonuses.services.b1 import load_bonus1, load_bonus1_by_webhook
from bonuses.services.b2 import load_bonus2, load_bonus2_by_webhook
from bonuses.services.save import save_bonuses

@app.task
def load_bonus1_task():
    load_bonus1()
@app.task
def load_bonus1_by_webhook_task():
    load_bonus1_by_webhook()
    
@app.task
def load_bonus2_task():
    load_bonus2()
@app.task
def load_bonus2_by_webhook_task():
    load_bonus2_by_webhook()

@app.task
def save_bonuses_by_webhook_task():
    save_bonuses()

