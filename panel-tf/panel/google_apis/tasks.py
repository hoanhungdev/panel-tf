from panel.celery import app
from google_apis.services.drive.main import give_permission

@app.task(bind=True, default_retry_delay=20 * 60)
def transfer_owner_task(self, file_id, email):
    try:
        give_permission(item_id=file_id, email=email, role='owner')
    except Exception as exc:
        self.retry(exc=exc)
        
@app.task(bind=True, default_retry_delay=20 * 60)
def give_permission_task(self, item_id: str, email: str, role: str):
    try:
        give_permission(item_id=item_id, email=email, role=role)
    except Exception as exc:
        self.retry(exc=exc)