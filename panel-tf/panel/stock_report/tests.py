from django.test import TestCase
from stock_report.services.main import update_table
# Create your tests here.

class TestCase(TestCase):

    #def test_update_table(self):
    #    spreadsheet_id = '11W4AUHf6fxJ8gk9HcNu0kEQevsdf70PceycwxhkzvbM'
    #    update_table_task.delay(spreadsheet_id)
    #    self.assertTrue(True)
        
    def test_debit_products(self):
        update_table()
        self.assertTrue(True)





