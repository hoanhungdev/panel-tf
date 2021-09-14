command = '/home/admin/code/panel-tf/venv/bin/gunicorn'
pythonpath = '/home/admin/code/panel-tf/panel'
bind = '127.0.0.1:8001'
workers = 5
user = 'admin'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'DJANGO_SETTINGS-MODULE=panel.settings'
