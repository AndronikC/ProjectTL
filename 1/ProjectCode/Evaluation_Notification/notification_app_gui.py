from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# --- SQLAlchemy Setup ---
Base = declarative_base()
engine = create_engine("sqlite:///study_platform.db")
Session = sessionmaker(bind=engine)
session = Session()

# --- Μοντέλα βάσης ---
class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    role = Column(String)
    notifications = relationship("Notification", back_populates="user")


class Notification(Base):
    __tablename__ = 'Notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.id"))
    content = Column(Text)
    date = Column(String)
    seen = Column(Integer, default=0)

    user = relationship("User", back_populates="notifications")


# --- Message Panel ---
class MessagePanel:
    def send_notification(self, user, notification):
        print(f"[MESSAGE] Sent to {user.email}: {notification.content}")
        user.notifications.append(notification)

    def send_reminder_notification(self, user, notification):
        print(f"[REMINDER] Reminder sent to {user.email} for: {notification.content}")


# --- Notification Management ---
class NotificationManagementPage:
    def __init__(self, msg_panel):
        self.msg_panel = msg_panel

    def set_notification(self, user, notification):
        self.msg_panel.send_notification(user, notification)
        session.add(notification)
        session.commit()

    def send_reminder_if_needed(self, user, notification):
        if not notification.seen:
            self.msg_panel.send_reminder_notification(user, notification)


# --- GUI ---
class NotificationGUI:
    def __init__(self, root, msg_panel, notif_mgmt):
        self.root = root
        self.root.title("Notification System")
        self.root.geometry("800x500")
        self.msg_panel = msg_panel
        self.notif_mgmt = notif_mgmt

        email_input = simpledialog.askstring("Είσοδος", "Εισάγετε email:")
        if not email_input:
            messagebox.showerror("Σφάλμα", "Δεν εισάγατε email.")
            root.destroy()
            return

        email_clean = email_input.strip().lower()
        self.user = session.query(User).filter(User.email.ilike(email_clean)).first()

        if not self.user:
            messagebox.showerror("Σφάλμα", "Ο χρήστης δεν βρέθηκε.")
            root.destroy()
            return

        # Πίνακας ειδοποιήσεων
        self.tree = ttk.Treeview(root, columns=("content", "date", "seen"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill=tk.BOTH)

        # Κουμπιά
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Ανανέωση", command=self.load_notifications).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Νέα Ειδοποίηση", command=self.send_notification).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Υπενθύμιση", command=self.send_reminder_to_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Διαγραφή Όλων", command=self.clear_notifications).pack(side=tk.LEFT, padx=5)

        self.load_notifications()

    def load_notifications(self):
        self.tree.delete(*self.tree.get_children())
        notifications = session.query(Notification).filter_by(user_id=self.user.id).all()
        for notif in notifications:
            seen_text = "Ναι" if notif.seen else "Όχι"
            self.tree.insert("", "end", iid=notif.id, values=(notif.content, notif.date, seen_text))

    def send_notification(self):
        msg = simpledialog.askstring("Ειδοποίηση", "Μήνυμα ειδοποίησης:")
        if msg:
            notif = Notification(
                user_id=self.user.id,
                content=msg,
                date=datetime.now().strftime("%Y-%m-%d"),
                seen=0
            )
            self.notif_mgmt.set_notification(self.user, notif)
            self.load_notifications()

    def send_reminder_to_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Προσοχή", "Επιλέξτε μια ειδοποίηση.")
            return

        notif_id = int(selected[0])
        notif = session.query(Notification).filter_by(id=notif_id).first()
        if notif:
            self.notif_mgmt.send_reminder_if_needed(self.user, notif)

    def clear_notifications(self):
        session.query(Notification).filter_by(user_id=self.user.id).delete()
        session.commit()
        self.load_notifications()


# Εκκίνηση εφαρμογής
def GUIApp():
    msg_panel = MessagePanel()
    notif_mgmt = NotificationManagementPage(msg_panel)

    root = tk.Tk()
    NotificationGUI(root, msg_panel, notif_mgmt)
    root.mainloop()


if __name__ == "__main__":
    GUIApp()
