import tkinter as tk
import unittest
from unittest.mock import MagicMock
from usecase4 import PaymentPage, Database, CURRENT_USER_ID

class PaymentPageTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Απόκρυψη GUI
        self.db = Database()
        self.page = PaymentPage(self.root, "Φοιτητής", self.db)

    def tearDown(self):
        self.page.window.destroy()
        self.root.destroy()

    def fill_valid_fields(self):
        self.page.card_number_entry.delete(0, tk.END)
        self.page.card_number_entry.insert(0, "1234567812345678")
        self.page.expiry_var.set("12/25")
        self.page.card_name_entry.delete(0, tk.END)
        self.page.card_name_entry.insert(0, "John Doe")

    def test_TC1_invalid_card_non_digit(self):
        self.page.card_number_entry.insert(0, "1234abcd5678abcd")
        self.page.validate_and_submit()
        self.assertEqual(self.page.card_number_error["text"], "Μόνο αριθμοί επιτρέπονται")
        print("✅ TC1 OK")

    def test_TC2_invalid_card_length(self):
        self.page.card_number_entry.insert(0, "12345678")
        self.page.validate_and_submit()
        self.assertEqual(self.page.card_number_error["text"], "Ο αριθμός πρέπει να περιέχει 16 ψηφία")
        print("✅ TC2 OK")

    def test_TC3_invalid_expiry_format(self):
        self.page.card_number_entry.insert(0, "1234567812345678")
        self.page.expiry_var.set("1255")  # Λάθος format
        self.page.card_name_entry.insert(0, "John Doe")
        self.page.validate_and_submit()
        self.assertEqual(self.page.expiry_error["text"], "Μορφή: MM/YY")
        print("✅ TC3 OK")

    def test_TC4_invalid_cardholder_name(self):
        self.page.card_number_entry.insert(0, "1234567812345678")
        self.page.expiry_var.set("12/25")
        self.page.card_name_entry.insert(0, "Γιάννης Παπαδόπουλος")  # μη λατινικό
        self.page.validate_and_submit()
        self.assertEqual(self.page.card_name_error["text"], "Μόνο λατινικοί χαρακτήρες")
        print("✅ TC4 OK")

    def test_TC5_existing_subscription(self):
        self.fill_valid_fields()
        self.db.userHasActiveSubscription = MagicMock(return_value=True)
        self.page.validate_and_submit()
        print("✅ TC5 OK – Υπάρχουσα συνδρομή (mocked)")

    def test_TC6_valid_payment_submission(self):
        self.fill_valid_fields()
        self.db.userHasActiveSubscription = MagicMock(return_value=False)
        self.db.insertSubscription = MagicMock()
        self.page.validate_and_submit()
        self.db.insertSubscription.assert_called_once_with(CURRENT_USER_ID, "Φοιτητής")
        print("✅ TC6 OK – Εγγραφή επιτυχής")

if __name__ == '__main__':
    unittest.main()
