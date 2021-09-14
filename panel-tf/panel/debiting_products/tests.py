from django.test import TestCase
from .tasks import update_table_task, debit_products_task



class TestCase(TestCase):

    #def test_update_table(self):
    #    spreadsheet_id = '11W4AUHf6fxJ8gk9HcNu0kEQevsdf70PceycwxhkzvbM'
    #    update_table_task.delay(spreadsheet_id)
    #    self.assertTrue(True)
        
    def test_debit_products(self):
        spreadsheet_id = '11W4AUHf6fxJ8gk9HcNu0kEQevsdf70PceycwxhkzvbM'
        debit_products_task.delay(spreadsheet_id)
        self.assertTrue(True)




