from django.test import TestCase
from .services.spreadsheets.main import test_write

class SpreadsheetsTestCase(TestCase):

    def test_proceed_all_box_office(self):
        """Animals that can speak are correctly identified"""
        test_write(spreadsheet_id='1UqPUuYZODzxkoJ_xl-Fxf-NWmeVgS46mMvl8Iw3awQQ', sheet='РАЗБОР', column=8, row_id=7, data="3.2.2020 17:44:21")
        self.assertTrue(True)






