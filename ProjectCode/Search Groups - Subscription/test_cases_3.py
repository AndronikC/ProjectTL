# test_cases_3.py
# Μονάδες Ελέγχου για την UIManager
import sqlite3
import tkinter as tk
import unittest
from unittest.mock import MagicMock
from usecase3 import UIManager, DatabaseManager

class FakeRoot:
    def deiconify(self):
        pass

class FakeEntry:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value

class UITestCase(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.ui = UIManager(self.root)
        self.ui.db = DatabaseManager()
        self.ui.department_entry = FakeEntry("Πληροφορική")
        self.ui.course_entry = FakeEntry("Αλγόριθμοι")
        self.ui.mode_var = MagicMock()
        self.ui.mode_var.get = MagicMock(return_value="εξ αποστάσεως")
        self.ui.result_list = MagicMock()
        self.ui.result_list.get_children = MagicMock(return_value=[])
        self.ui.result_list.delete = MagicMock()
        self.ui.result_list.insert = MagicMock()

    def test_getGroups_no_criteria(self):
        self.ui.getGroups(False)
        print("OK - test_getGroups_no_criteria")

    def test_getGroups_with_criteria(self):
        self.ui.getGroups(True)
        print("OK - test_getGroups_with_criteria")

    def test_displayGroupList_empty(self):
        self.ui.returnNoGroupsFound = MagicMock()
        self.ui.displayGroupList([])
        self.ui.returnNoGroupsFound.assert_called_once()
        print("OK - test_displayGroupList_empty")

    def test_returnAvailableGroups(self):
        data = [1, 2, 3]
        result = self.ui.returnAvailableGroups(data)
        self.assertEqual(result, data)
        print("OK - test_returnAvailableGroups")

    def test_getGroupsCriteria(self):
        criteria = self.ui.getGroupsCriteria()
        self.assertEqual(criteria, ("Πληροφορική", "Αλγόριθμοι", "εξ αποστάσεως"))
        print("OK - test_getGroupsCriteria")

        def tearDown(self):
            self.root.destroy()

if __name__ == '__main__':
    unittest.main()
