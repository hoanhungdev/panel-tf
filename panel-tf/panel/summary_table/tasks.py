from panel.celery import app
from summary_table.services.sheets.dds import load_dds
from summary_table.services.sheets.debitorka import load_debitorka
from summary_table.services.sheets.planovye_platezhi import load_planovye_platezhi
from summary_table.services.sheets.planovye_postupleniya import load_planovye_postupleniya
from summary_table.services.sheets.beznal import load_beznal
from summary_table.services.sheets.nal import load_nal
from summary_table.services.sheets.reestr_proektov import load_reestr_proektov
from summary_table.services.sheets.vzaimoraschety import load_vzaimoraschety
from summary_table.services.sheets.budgety_adm import load_budgety_adm
from summary_table.services.sheets.budget_proekta import load_budget_proekta
from summary_table.services.sheets.zakrytie_proektov import load_zakrytie_proektov

@app.task
def load_dds_task():
    load_dds()
@app.task
def load_dds_webhook_task():
    load_dds()
    
@app.task
def load_debitorka_task():
    load_debitorka()
@app.task
def load_debitorka_webhook_task():
    load_debitorka()
    
@app.task
def load_planovye_platezhi_task():
    load_planovye_platezhi()
@app.task
def load_planovye_platezhi_webhook_task():
    load_planovye_platezhi()

@app.task
def load_planovye_postupleniya_task():
    load_planovye_postupleniya()
@app.task
def load_planovye_postupleniya_webhook_task():
    load_planovye_postupleniya()

@app.task
def load_beznal_task():
    load_beznal()
@app.task
def load_beznal_webhook_task():
    load_beznal()
    
@app.task
def load_nal_task():
    load_nal()
@app.task
def load_nal_webhook_task():
    load_nal()
    
@app.task
def load_reestr_proektov_task():
    load_reestr_proektov()
@app.task
def load_reestr_proektov_webhook_task():
    load_reestr_proektov()
    
@app.task
def load_vzaimoraschety_task():
    load_vzaimoraschety()
@app.task
def load_vzaimoraschety_webhook_task():
    load_vzaimoraschety()
    
@app.task
def load_zakrytie_proektov_task():
    load_zakrytie_proektov()
@app.task
def load_zakrytie_proektov_webhook_task():
    load_zakrytie_proektov()


    
@app.task
def load_budgety_adm_task():
    load_budgety_adm()
@app.task
def load_budget_proekta_task():
    load_budget_proekta()


