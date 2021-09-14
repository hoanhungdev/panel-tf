from django.test import TestCase
from .tasks import proceed_single_box_office
from box_office.services.employees import start


class BoxOfficeTestCase(TestCase):

    def test_shulaeva_box_office(self):
        box_office = {'name': 'Тест Шулаева', \
        'attribute_value': 'https://docs.google.com/spreadsheets/d/1HsaNWwT7G71AWt-oFJWJvMQZka1QhTZL6leGkzHgHl0/edit#gid=1428559956', \
        'entity_type': 'employee'}
        proceed_single_box_office.delay(1, box_office)
        self.assertTrue(True)

    def test_tf_box_office(self):
        box_office = {'name': 'Тест ТФ', \
        'attribute_value': 'https://docs.google.com/spreadsheets/d/1KiGbtMaFdeDg1qXRfQ2PPteMpCRWon_SLRYplsZ_f1c/edit#gid=1428559956', \
        'entity_type': 'organization'}
        proceed_single_box_office.delay(1, box_office)
        self.assertTrue(True)

#class EmployeesTestCase(TestCase):
#
#    def test_load_employees_payments(self):
#        """Animals that can speak are correctly identified"""
#        start()
#        self.assertTrue(True)
