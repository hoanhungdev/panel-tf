from django.test import TestCase
from .tasks import get_bank_statement_celery_task

class BoxOfficeTestCase(TestCase):

    def test_get_bank_statement(self):
        get_bank_statement_celery_task.delay()
        self.assertTrue(True)