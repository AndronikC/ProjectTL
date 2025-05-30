import sqlite3
import re
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
from study_groups import show_study_groups_screen

DB_PATH = "users.db"
PROFILE_PIC_FOLDER = "profile_pics"
BIO_MAX_LENGTH = 500

class User:
    def __init__(self, user_id, first_name, last_name, email, profile_pic, bio, phone, password):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.profile_pic = profile_pic
        self.bio = bio
        self.phone = phone
        self.password = password

class UserDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            profile_pic TEXT,
            bio TEXT,
            phone TEXT,
            password TEXT
        )
        """)
        self.conn.commit()

    def add_user(self, user: User):
        self.conn.execute("""
        INSERT INTO users (first_name, last_name, email, profile_pic, bio, phone, password)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user.first_name, user.last_name, user.email, user.profile_pic, user.bio, user.phone, user.password))
        self.conn.commit()

    def get_user_by_email(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if row:
            return User(*row)
        return None

    def update_user(self, user: User):
        self.conn.execute("""
        UPDATE users SET first_name=?, last_name=?, email=?, profile_pic=?, bio=?, phone=?, password=?
        WHERE id=?
        """, (user.first_name, user.last_name, user.email, user.profile_pic, user.bio, user.phone, user.password, user.user_id))
        self.conn.commit()

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_phone(phone):
    return phone == "" or (phone.isdigit() and len(phone) == 10)

def validate_bio(bio):
    return len(bio) <= BIO_MAX_LENGTH

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Διαχείριση Προφίλ")
        self.geometry("500x600")
        self.db = UserDB()
        self.user = None
        self.show_main_menu()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear()
        logo_path = "studyswap_logo.png"
        if os.path.exists(logo_path):
            # Resize image using PIL
            img = Image.open(logo_path)
            img = img.resize((180, 60), Image.LANCZOS)  # Μπορείς να αλλάξεις τις διαστάσεις
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(self, image=self.logo_img)
            logo_label.pack(pady=20)
        else:
            ttk.Label(self, text="StudySwap", font=("Arial", 18)).pack(pady=20)
        ttk.Button(self, text="Εγγραφή", command=self.show_register).pack(pady=10)
        ttk.Button(self, text="Σύνδεση", command=self.show_login).pack(pady=10)
        ttk.Button(self, text="Έξοδος", command=self.destroy).pack(pady=10)

    def show_register(self):
        self.clear()
        entries = {}
        fields = [
            ("Όνομα", "first_name"),
            ("Επώνυμο", "last_name"),
            ("Email", "email"),
            ("Τηλέφωνο (10 ψηφία)", "phone"),
            (f"Βιογραφικό (μέγιστο {BIO_MAX_LENGTH} χαρακτήρες)", "bio"),
            ("Κωδικός", "password"),
            ("Επιβεβαίωση Κωδικού", "password2"),
        ]
        ttk.Label(self, text="Εγγραφή", font=("Arial", 16)).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(pady=10)
        for label, key in fields:
            ttk.Label(frame, text=label).pack()
            entry = ttk.Entry(frame, show="*" if "κωδ" in label.lower() else "")
            entry.pack()
            entries[key] = entry
        ttk.Label(frame, text="Εικόνα Προφίλ").pack()
        pic_var = tk.StringVar()
        pic_entry = ttk.Entry(frame, textvariable=pic_var)
        pic_entry.pack()
        def browse_pic():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
            if path:
                if not os.path.exists(PROFILE_PIC_FOLDER):
                    os.makedirs(PROFILE_PIC_FOLDER)
                filename = os.path.basename(path)
                dest = os.path.join(PROFILE_PIC_FOLDER, filename)
                with open(path, "rb") as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                pic_var.set(dest)
        ttk.Button(frame, text="Επιλογή εικόνας...", command=browse_pic).pack()
        # Προσθήκη ενημερωτικού label για τα υποχρεωτικά πεδία
        ttk.Label(self, text="* Υποχρεωτικά πεδία: Όνομα, Επώνυμο, Email, Κωδικός", foreground="red").pack(pady=5)
        def submit():
            first_name = entries["first_name"].get()
            last_name = entries["last_name"].get()
            email = entries["email"].get()
            phone = entries["phone"].get()
            bio = entries["bio"].get()
            password = entries["password"].get()
            password2 = entries["password2"].get()
            profile_pic = pic_var.get()
            if not validate_email(email):
                messagebox.showerror("Σφάλμα", "Μη έγκυρο email.")
                return
            if self.db.get_user_by_email(email):
                messagebox.showerror("Σφάλμα", "Το email χρησιμοποιείται ήδη.")
                return
            if phone and not validate_phone(phone):
                messagebox.showerror("Σφάλμα", "Μη έγκυρος αριθμός τηλεφώνου.")
                return
            if not validate_bio(bio):
                messagebox.showerror("Σφάλμα", "Το βιογραφικό είναι πολύ μεγάλο.")
                return
            if password != password2:
                messagebox.showerror("Σφάλμα", "Οι κωδικοί δεν ταιριάζουν.")
                return
            user = User(None, first_name, last_name, email, profile_pic, bio, phone, password)
            self.db.add_user(user)
            messagebox.showinfo("Επιτυχία", "Επιτυχής εγγραφή!")
            self.show_main_menu()
        ttk.Button(self, text="Εγγραφή", command=submit).pack(pady=10)
        ttk.Button(self, text="Πίσω", command=self.show_main_menu).pack()

    def show_login(self):
        self.clear()
        ttk.Label(self, text="Σύνδεση", font=("Arial", 16)).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(pady=10)
        ttk.Label(frame, text="Email").pack()
        email_entry = ttk.Entry(frame)
        email_entry.pack()
        ttk.Label(frame, text="Κωδικός").pack()
        password_entry = ttk.Entry(frame, show="*")
        password_entry.pack()
        def submit():
            email = email_entry.get()
            password = password_entry.get()
            user = self.db.get_user_by_email(email)
            if user and user.password == password:
                self.user = user
                self.show_profile()
            else:
                messagebox.showerror("Σφάλμα", "Λάθος email ή κωδικός.")
        ttk.Button(self, text="Σύνδεση", command=submit).pack(pady=10)
        ttk.Button(self, text="Πίσω", command=self.show_main_menu).pack()

    def show_profile(self):
        self.clear()
        # Εμφάνιση ονόματος και επωνύμου ως τίτλος
        full_name = f"{self.user.first_name} {self.user.last_name}"
        ttk.Label(self, text=full_name, font=("Arial", 16)).pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack(pady=10)

        # Εικόνα προφίλ αριστερά
        if self.user.profile_pic and os.path.exists(self.user.profile_pic):
            img = Image.open(self.user.profile_pic)
            img = img.resize((80, 80), Image.LANCZOS)
            self.profile_img = ImageTk.PhotoImage(img)
            img_label = ttk.Label(frame, image=self.profile_img)
            img_label.grid(row=0, column=0, rowspan=5, padx=10, pady=5)
        else:
            img_label = ttk.Label(frame, text="Χωρίς εικόνα", width=12)
            img_label.grid(row=0, column=0, rowspan=5, padx=10, pady=5)

        # Στοιχεία χρήστη δεξιά
        info = (
            f"Email: {self.user.email}\n"
            f"Τηλέφωνο: {self.user.phone}\n"
            f"Βιογραφικό: {self.user.bio}"
        )
        ttk.Label(frame, text=info, justify="left").grid(row=0, column=1, sticky="w")

        ttk.Button(self, text="Επεξεργασία Προφίλ", command=self.show_edit_profile).pack(pady=5)
        ttk.Button(self, text="Ομάδες Μελέτης", command=self.open_study_groups).pack(pady=5)
        ttk.Button(self, text="Αλλαγή κωδικού", command=self.show_change_password).pack(pady=5)
        ttk.Button(self, text="Αποσύνδεση", command=self.show_main_menu).pack(pady=5)

    def show_edit_profile(self):
        self.clear()
        entries = {}
        fields = [
            ("Όνομα", "first_name", self.user.first_name),
            ("Επώνυμο", "last_name", self.user.last_name),
            ("Email", "email", self.user.email),
            ("Τηλέφωνο (10 ψηφία)", "phone", self.user.phone),
            (f"Βιογραφικό (μέγιστο {BIO_MAX_LENGTH} χαρακτήρες)", "bio", self.user.bio),
        ]
        ttk.Label(self, text="Επεξεργασία Προφίλ", font=("Arial", 16)).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(pady=10)
        for label, key, val in fields:
            ttk.Label(frame, text=label).pack()
            entry = ttk.Entry(frame)
            entry.insert(0, val)
            entry.pack()
            entries[key] = entry
        ttk.Label(frame, text="Εικόνα Προφίλ").pack()
        pic_var = tk.StringVar(value=self.user.profile_pic)
        pic_entry = ttk.Entry(frame, textvariable=pic_var)
        pic_entry.pack()
        def browse_pic():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
            if path:
                if not os.path.exists(PROFILE_PIC_FOLDER):
                    os.makedirs(PROFILE_PIC_FOLDER)
                filename = os.path.basename(path)
                dest = os.path.join(PROFILE_PIC_FOLDER, filename)
                with open(path, "rb") as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                pic_var.set(dest)
        ttk.Button(frame, text="Επιλογή εικόνας...", command=browse_pic).pack()
        def save():
            first_name = entries["first_name"].get()
            last_name = entries["last_name"].get()
            email = entries["email"].get()
            phone = entries["phone"].get()
            bio = entries["bio"].get()
            profile_pic = pic_var.get()
            errors = []
            if not validate_email(email):
                errors.append("Μη έγκυρο email.")
            if self.db.get_user_by_email(email) and self.db.get_user_by_email(email).user_id != self.user.user_id:
                errors.append("Το email χρησιμοποιείται ήδη.")
            if phone and not validate_phone(phone):
                errors.append("Μη έγκυρος αριθμός τηλεφώνου.")
            if not validate_bio(bio):
                errors.append("Το βιογραφικό είναι πολύ μεγάλο.")
            if errors:
                messagebox.showerror("Σφάλμα", "\n".join(errors))
                return
            self.user.first_name = first_name
            self.user.last_name = last_name
            self.user.email = email
            self.user.phone = phone
            self.user.bio = bio
            self.user.profile_pic = profile_pic
            self.db.update_user(self.user)
            messagebox.showinfo("Επιτυχία", "Τα στοιχεία αποθηκεύτηκαν.")
            self.show_profile()
        ttk.Button(self, text="Αποθήκευση", command=save).pack(pady=10)
        ttk.Button(self, text="Ακύρωση", command=self.show_profile).pack()

    def show_change_password(self):
        self.clear()
        ttk.Label(self, text="Αλλαγή Κωδικού", font=("Arial", 16)).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(pady=10)
        ttk.Label(frame, text="Τρέχων Κωδικός").pack()
        old_entry = ttk.Entry(frame, show="*")
        old_entry.pack()
        ttk.Label(frame, text="Νέος Κωδικός").pack()
        new_entry = ttk.Entry(frame, show="*")
        new_entry.pack()
        ttk.Label(frame, text="Επιβεβαίωση Νέου Κωδικού").pack()
        new2_entry = ttk.Entry(frame, show="*")
        new2_entry.pack()
        def change():
            old = old_entry.get()
            new = new_entry.get()
            new2 = new2_entry.get()
            if old != self.user.password:
                messagebox.showerror("Σφάλμα", "Λάθος τρέχων κωδικός.")
                return
            if new != new2:
                messagebox.showerror("Σφάλμα", "Οι νέοι κωδικοί δεν ταιριάζουν.")
                return
            self.user.password = new
            self.db.update_user(self.user)
            messagebox.showinfo("Επιτυχία", "Ο κωδικός άλλαξε επιτυχώς.")
            self.show_profile()
        ttk.Button(self, text="Αλλαγή", command=change).pack(pady=10)
        ttk.Button(self, text="Ακύρωση", command=self.show_profile).pack()

    def open_study_groups(self):
        show_study_groups_screen(self, self.user)

if __name__ == "__main__":
    app = App()
    app.mainloop()