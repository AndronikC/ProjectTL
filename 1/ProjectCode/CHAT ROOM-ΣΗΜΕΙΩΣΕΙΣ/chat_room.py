import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import hashlib
import re
import datetime
from sqlalchemy.sql import or_
import sqlite3

# Βεβαιώσου ότι υπάρχει το πεδίο is_available στους καθηγητές και όλοι οι κωδικοί είναι hashed
conn = sqlite3.connect("study_platform.db")
cur = conn.cursor()
cur.execute("SELECT id, password FROM Users")
for user_id, pwd in cur.fetchall():
    if len(pwd) != 64:
        hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()
        cur.execute("UPDATE Users SET password = ? WHERE id = ?", (hashed_pwd, user_id))
try:
    cur.execute("ALTER TABLE Users ADD COLUMN is_available INTEGER DEFAULT 1")
except sqlite3.OperationalError:
    pass
conn.commit()
conn.close()

Base = declarative_base()
engine = create_engine("sqlite:///study_platform.db")
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    department_id = Column(Integer)
    is_available = Column(Integer, default=1)

class Message(Base):
    __tablename__ = "Messages"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer)
    receiver_id = Column(Integer)
    timestamp = Column(String)
    content = Column(Text)

class Course(Base):
    __tablename__ = "Courses"
    id = Column(Integer, primary_key=True)
    title = Column(String)

class StudyGroup(Base):
    __tablename__ = "StudyGroups"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer)
    creator_id = Column(Integer)

class Notification(Base):
    __tablename__ = "Notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    content = Column(Text)
    date = Column(String)
    seen = Column(Integer, default=0)

# -- Helpers --
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@(?:gmail|yahoo)\.com$", email)

# -- Refactored Components based on Lifelines --
class CourseSelectionPage:
    def __init__(self, app):
        self.app = app

    def display(self):
        self.app.select_course()

class TeacherSelectionPage:
    def __init__(self, app):
        self.app = app

    def getteachers(self, course_id):
        self.app.select_teacher(course_id)

class ChatButton:
    def __init__(self, app):
        self.app = app

    def openChatRoom(self, other_id):
        self.app.check_availability_and_open_chat(other_id)

class ChatRoom:
    def __init__(self, app):
        self.app = app

    def returnChatReady(self, other_id):
        self.app.open_chatroom_with(other_id)

class NotificationSystem:
    @staticmethod
    def notifyTeacher():
        pass

    @staticmethod
    def notifyUser():
        pass

class UnavailableTeacherMessage:
    @staticmethod
    def display():
        messagebox.showinfo("Μη διαθέσιμος", "Ο καθηγητής είναι προσωρινά μη διαθέσιμος.")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Platform - Chat Room")
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

        if user.role == "tutor":
            def toggle_availability():
                self.user.is_available = 1 - self.user.is_available
                session.commit()
                status_label.config(text=f"Διαθεσιμότητα: {'Ναι' if self.user.is_available else 'Όχι'}")
            status_label = tk.Label(self.root, text=f"Διαθεσιμότητα: {'Ναι' if self.user.is_available else 'Όχι'}")
            status_label.pack()
            tk.Button(self.root, text="Εναλλαγή Διαθεσιμότητας", command=toggle_availability).pack()

            tk.Label(self.root, text="Φοιτητές που σου έστειλαν μηνύματα:").pack()
            senders = session.query(Message.sender_id).filter_by(receiver_id=user.id).distinct().all()
            for s in senders:
                sender = session.query(User).get(s[0])
                if sender:
                    btn = tk.Button(self.root, text=f"{sender.first_name} {sender.last_name}",
                                    command=lambda s_id=sender.id: self.open_chatroom_with(s_id))
                    btn.pack()
        else:
            tk.Button(self.root, text="Chat με καθηγητή", command=lambda: CourseSelectionPage(self).display()).pack()

        tk.Button(self.root, text="Logout", command=self.create_login_screen).pack()

    def select_course(self):
        self.clear_screen()
        tk.Label(self.root, text="Επέλεξε μάθημα:").pack()
        course_ids = session.query(StudyGroup.course_id).distinct().all()
        course_ids = [c[0] for c in course_ids]
        courses = session.query(Course).filter(Course.id.in_(course_ids)).all()
        for course in courses:
            tk.Button(self.root, text=course.title,
                      command=lambda cid=course.id: TeacherSelectionPage(self).getteachers(cid)).pack()
        tk.Button(self.root, text="Back", command=lambda: self.create_main_screen(self.user)).pack()

    def select_teacher(self, course_id):
        self.clear_screen()
        tk.Label(self.root, text="Επέλεξε καθηγητή:").pack()
        tutor_ids = session.query(StudyGroup.creator_id).filter_by(course_id=course_id).distinct().all()
        tutor_ids = [t[0] for t in tutor_ids]
        if not tutor_ids:
            tk.Label(self.root, text="Δεν υπάρχουν διαθέσιμοι καθηγητές για το συγκεκριμένο μάθημα.").pack()
        else:
            tutors = session.query(User).filter(User.id.in_(tutor_ids), User.role == 'tutor').all()
            for tutor in tutors:
                label = f"{tutor.first_name} {tutor.last_name}"
                if tutor.is_available == 0:
                    label += " (Μη διαθέσιμος)"
                tk.Button(self.root, text=label,
                          command=lambda tid=tutor.id: ChatButton(self).openChatRoom(tid)).pack()
        tk.Button(self.root, text="Back", command=lambda: self.create_main_screen(self.user)).pack()

    def check_availability_and_open_chat(self, other_id):
        partner = session.query(User).get(other_id)
        if partner and partner.is_available == 0:
            UnavailableTeacherMessage.display()
        ChatRoom(self).returnChatReady(other_id)

    def open_chatroom_with(self, other_id):
        chat = tk.Toplevel(self.root)
        chat.title("Chatroom")
        chat.geometry("400x400")
        self.chat_partner_id = other_id
        self.chat_log = tk.Text(chat, state='disabled')
        self.chat_log.pack(expand=True, fill='both')
        entry_frame = tk.Frame(chat)
        entry_frame.pack(fill='x')
        self.chat_entry = tk.Entry(entry_frame)
        self.chat_entry.pack(side='left', fill='x', expand=True)
        tk.Button(entry_frame, text="Send", command=self.send_message_to_partner).pack(side='right')
        self.load_messages_with()

    def load_messages_with(self):
        self.chat_log.config(state='normal')
        self.chat_log.delete(1.0, tk.END)
        messages = session.query(Message).filter(
            or_(
                (Message.sender_id == self.user.id) & (Message.receiver_id == self.chat_partner_id),
                (Message.sender_id == self.chat_partner_id) & (Message.receiver_id == self.user.id)
            )
        ).order_by(Message.timestamp).all()
        for msg in messages:
            sender = session.query(User).get(msg.sender_id)
            if sender:
                self.chat_log.insert(tk.END, f"{sender.first_name} {sender.last_name}: {msg.content}\n")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def send_message_to_partner(self):
        content = self.chat_entry.get()
        if not content:
            return
        msg = Message(sender_id=self.user.id, receiver_id=self.chat_partner_id,
                      timestamp=str(datetime.datetime.now()), content=content)
        session.add(msg)
        notif = Notification(user_id=self.chat_partner_id, content="Νέο μήνυμα στο Chat",
                             date=str(datetime.datetime.now()))
        session.add(notif)
        session.commit()
        self.chat_entry.delete(0, tk.END)
        self.load_messages_with()

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

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()

