from startpage.models import Auth
from bitrix.services.bitrix24 import Bitrix24


class BitrixException(Exception):
    pass

auth = Auth.get('bitrix')[0]
user_id = 165
base_url = f'https://tehnofasad.bitrix24.ru/rest/{user_id}/{auth}/'
bx = Bitrix24(base_url)
#auth1 = 'p6lm7o8p9g0d3gsk'
#base_url = f'https://b24-7xm7s0.bitrix24.ru/rest/1/{auth1}/'
#bx_test = Bitrix24(base_url)


date_template = '%Y-%m-%dT%H:%M:%S+03:00'
task_url_template = 'https://tehnofasad.bitrix24.ru/company/personal/user/165/tasks/task/view/'



