import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from chat_room import Base, User, hash_password, App  # ← άλλαξε εδώ το όνομα του αρχείου σου
import tkinter as tk

class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Σύνδεση με την ΚΑΝΟΝΙΚΗ βάση δεδομένων
        cls.engine = create_engine("sqlite:///study_platform.db")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        cls.session = cls.Session()

        # Διαγραφή χρήστη αν υπάρχει ήδη
        existing = cls.session.query(User).filter_by(email="testuser@gmail.com").first()
        if existing:
            cls.session.delete(existing)
            cls.session.commit()

        # Προσθήκη test χρήστη
        cls.test_user = User(
            first_name="Test",
            last_name="User",
            email="testuser@gmail.com",
            password=hash_password("testpass"),
            role="student",
            department_id=None
        )
        cls.session.add(cls.test_user)
        cls.session.commit()

    def setUp(self):
        self.root = tk.Tk()
        self.app = App(self.root)

        # Συμπλήρωση login στοιχείων
        self.app.email_entry.insert(0, "testuser@gmail.com")
        self.app.pass_entry.insert(0, "testpass")

    def test_login_success(self):
        # Εκτέλεση login
        self.app.login()

        # Έλεγχος για welcome label
        found = any(
            isinstance(w, tk.Label) and "Welcome Test User" in w.cget("text")
            for w in self.root.winfo_children()
        )
        self.assertTrue(found, "Login failed or welcome message not found")

    def tearDown(self):
        self.root.destroy()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.engine.dispose()

if __name__ == "__main__":
    unittest.main()
