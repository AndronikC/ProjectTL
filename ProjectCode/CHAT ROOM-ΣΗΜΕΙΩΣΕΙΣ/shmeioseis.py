import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import hashlib
import re
import os

Base = declarative_base()
engine = create_engine("sqlite:///study_platform.db")
Session = sessionmaker(bind=engine)
session = Session()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@(?:gmail|yahoo)\.com$", email)

class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    department_id = Column(Integer)

class Course(Base):
    __tablename__ = "Courses"
    id = Column(Integer, primary_key=True)
    title = Column(String)

class Note(Base):
    __tablename__ = "Notes"
    id = Column(Integer, primary_key=True)
    uploader_id = Column(Integer)
    course_id = Column(Integer)
    title = Column(String)
    file_path = Column(String)
    is_locked = Column(Integer, default=0)
    is_paid = Column(Integer, default=0)

class NotesService:
    @staticmethod
    def getNoteList(course_id, filter_paid=None, filter_free=None):
        query = session.query(Note).filter_by(course_id=course_id)
        if filter_paid:
            query = query.filter_by(is_paid=1)
        if filter_free:
            query = query.filter_by(is_paid=0)
        return query.all()

class FilterManager:
    @staticmethod
    def manage_filters():
        # Placeholder για πιθανή επέκταση φιλτραρίσματος
        return

class PaymentPage:
    @staticmethod
    def initiate_payment():
        return True

class PaymentError:
    @staticmethod
    def show():
        messagebox.showerror("Σφάλμα Πληρωμής", "Αποτυχία πληρωμής.")

class NotesPage:
    def __init__(self, app):
        self.app = app

    def display(self):
        self.app.search_notes()

    def displayNoResultMessage(self):
        tk.Label(self.app.root, text="Δεν βρέθηκαν σημειώσεις.").pack()
        tk.Button(self.app.root, text="Πίσω", command=self.app.search_notes).pack()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Platform")
        self.root.geometry("600x400")
        self.create_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()
        tk.Label(self.root, text="Password:").pack()
        self.pass_entry = tk.Entry(self.root, show="*")
        self.pass_entry.pack()
        tk.Button(self.root, text="Login", command=self.login).pack()
        tk.Button(self.root, text="Register", command=self.create_register_screen).pack()

    def create_register_screen(self):
        self.clear_screen()
        self.entries = {}
        for field in ["First Name", "Last Name", "Email", "Password", "Role"]:
            tk.Label(self.root, text=field + ":").pack()
            entry = tk.Entry(self.root, show="*" if field == "Password" else None)
            entry.pack()
            self.entries[field] = entry
        tk.Button(self.root, text="Submit", command=self.register).pack()
        tk.Button(self.root, text="Back", command=self.create_login_screen).pack()

    def create_main_screen(self, user):
        self.clear_screen()
        self.user = user
        tk.Label(self.root, text=f"Welcome {user.first_name} {user.last_name} ({user.role})").pack()

        tk.Button(self.root, text="Αναζήτηση Σημειώσεων", command=lambda: NotesPage(self).display()).pack()
        tk.Button(self.root, text="Logout", command=self.create_login_screen).pack()

    def search_notes(self):
        self.clear_screen()

        tk.Label(self.root, text="Επιλέξτε Μάθημα:").pack()
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.pack()

        self.filter_paid = tk.IntVar()
        self.filter_free = tk.IntVar()
        tk.Checkbutton(self.root, text="Μόνο επί πληρωμή", variable=self.filter_paid).pack()
        tk.Checkbutton(self.root, text="Μόνο δωρεάν", variable=self.filter_free).pack()
        tk.Button(self.root, text="Αναζήτηση", command=self.apply_filters).pack()

        self.course_buttons_frame = tk.Frame(self.root)
        self.course_buttons_frame.pack()
        self.load_course_buttons()

        tk.Button(self.root, text="Πίσω", command=lambda: self.create_main_screen(self.user)).pack()

    def load_course_buttons(self):
        for widget in self.course_buttons_frame.winfo_children():
            widget.destroy()

        courses = session.query(Course).all()
        for course in courses:
            tk.Button(self.course_buttons_frame, text=course.title,
                      command=lambda cid=course.id: self.display_notes_for_course(cid)).pack()

    def apply_filters(self):
        self.clear_screen()
        self.search_notes()

    def display_notes_for_course(self, course_id):
        self.clear_screen()
        tk.Label(self.root, text="Διαθέσιμες Σημειώσεις:").pack()

        FilterManager.manage_filters()
        notes = NotesService.getNoteList(course_id, self.filter_paid.get(), self.filter_free.get())

        if not notes:
            NotesPage(self).displayNoResultMessage()
            return

        for note in notes:
            note_info = f"{note.title} - {'Δωρεάν' if note.is_paid == 0 else 'Επί πληρωμή'}"
            tk.Button(self.root, text=note_info, command=lambda n=note: self.open_note(n)).pack()

        tk.Button(self.root, text="Πίσω", command=self.search_notes).pack()

    def open_note(self, note):
        if note.is_paid == 1:
            self.clear_screen()
            tk.Label(self.root, text="Αυτή η σημείωση είναι επί πληρωμή.").pack()
            tk.Label(self.root, text="Για να αποκτήσετε πρόσβαση, προχωρήστε σε πληρωμή συνδρομής.").pack()
            tk.Button(self.root, text="Πληρωμή Συνδρομής", command=self.payment_screen).pack()
            tk.Button(self.root, text="Πίσω", command=self.search_notes).pack()
        else:
            messagebox.showinfo("Προβολή Σημείωσης", f"Τίτλος: {note.title}\nΑρχείο: {os.path.basename(note.file_path)}")

    def payment_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Ολοκληρώστε την πληρωμή 6.99€ για πρόσβαση στις επί πληρωμή σημειώσεις.").pack()
        tk.Button(self.root, text="Πληρωμή", command=self.complete_payment).pack()
        tk.Button(self.root, text="Πίσω", command=self.create_main_screen).pack()

    def complete_payment(self):
        success = PaymentPage.initiate_payment()
        if success:
            messagebox.showinfo("Επιτυχία", "Η πληρωμή ολοκληρώθηκε με επιτυχία! Έχετε πλέον πρόσβαση στις σημειώσεις.")
            self.create_main_screen(self.user)
        else:
            PaymentError.show()

    def login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        user = session.query(User).filter_by(email=email).first()
        if user and user.password == hash_password(password):
            self.create_main_screen(user)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        first = self.entries["First Name"].get()
        last = self.entries["Last Name"].get()
        email = self.entries["Email"].get()
        password = self.entries["Password"].get()
        role = self.entries["Role"].get().lower()

        if not all([first, last, email, password, role]):
            messagebox.showerror("Error", "All fields are required")
            return
        if role not in ["student", "tutor"]:
            messagebox.showerror("Error", "Role must be 'student' or 'tutor'")
            return
        if not is_valid_email(email):
            messagebox.showerror("Error", "Invalid email")
            return
        if session.query(User).filter_by(email=email).first():
            messagebox.showerror("Error", "Email already registered")
            return

        user = User(
            first_name=first,
            last_name=last,
            email=email,
            password=hash_password(password),
            role=role,
            department_id=None
        )
        session.add(user)
        session.commit()
        self.create_main_screen(user)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
