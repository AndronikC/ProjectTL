import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shmeioseis import Base, User, Course, Note, hash_password, App
import tkinter as tk

class TestNoteAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Σύνδεση με πραγματική βάση
        cls.engine = create_engine("sqlite:///study_platform.db")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        cls.session = cls.Session()

        # Καθαρισμός προηγούμενων δεδομένων (προαιρετικό)
        cls.session.query(User).filter_by(email="teststudent@gmail.com").delete()
        cls.session.query(Course).filter_by(title="Δοκιμαστικό Μάθημα").delete()
        cls.session.commit()

        # Προσθήκη test χρήστη
        cls.test_user = User(
            first_name="Test",
            last_name="Student",
            email="teststudent@gmail.com",
            password=hash_password("testpass"),
            role="student",
            department_id=None
        )
        cls.session.add(cls.test_user)
        cls.session.commit()

        # Προσθήκη μαθήματος
        cls.test_course = Course(title="Δοκιμαστικό Μάθημα")
        cls.session.add(cls.test_course)
        cls.session.commit()

        # Προσθήκη σημείωσης
        cls.test_note = Note(
            uploader_id=cls.test_user.id,
            course_id=cls.test_course.id,
            title="Σημείωση Test",
            file_path="path/to/fake_note.pdf",
            is_paid=0
        )
        cls.session.add(cls.test_note)
        cls.session.commit()

    def setUp(self):
        self.root = tk.Tk()
        self.app = App(self.root)

        # Εισαγωγή credentials
        self.app.email_entry.insert(0, "teststudent@gmail.com")
        self.app.pass_entry.insert(0, "testpass")

    def test_login_and_course_display(self):
        self.app.login()

        # Έλεγχος ετικέτας welcome
        welcome_found = any(
            isinstance(w, tk.Label) and "Welcome Test Student" in w.cget("text")
            for w in self.root.winfo_children()
        )
        self.assertTrue(welcome_found, "Login failed or welcome not shown")

        # Προσομοίωση αναζήτησης μαθημάτων
        self.app.search_notes()

        course_titles = [
            w.cget("text") for w in self.app.course_buttons_frame.winfo_children()
            if isinstance(w, tk.Button)
        ]
        self.assertIn("Δοκιμαστικό Μάθημα", course_titles, "Course not displayed in search")

    def tearDown(self):
        self.root.destroy()

    @classmethod
    def tearDownClass(cls):
        cls.session.query(Note).filter_by(title="Σημείωση Test").delete()
        cls.session.query(Course).filter_by(title="Δοκιμαστικό Μάθημα").delete()
        cls.session.query(User).filter_by(email="teststudent@gmail.com").delete()
        cls.session.commit()
        cls.session.close()
        cls.engine.dispose()

if __name__ == "__main__":
    unittest.main()
