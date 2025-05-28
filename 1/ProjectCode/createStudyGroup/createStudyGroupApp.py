import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import mysql.connector
import re
from datetime import datetime

# Define color palette
BG_COLOR = "#fefefe"
PRIMARY_COLOR = "#4078c0"
PRIMARY_ACTIVE = "#5fa8d3"
SECONDARY_COLOR = "#b2bec3"
SECONDARY_ACTIVE = "#636e72"
SUCCESS_COLOR = "#00b894"
SUCCESS_ACTIVE = "#00cec9"
WARNING_COLOR = "#fdcb6e"
WARNING_ACTIVE = "#ffeaa7"
TEXT_COLOR = "#222f3e"
INPUT_BG = "#dff9fb"
INPUT_FG = "#222f3e"
ADD_BTN_COLOR = "#0984e3"
ADD_BTN_ACTIVE = "#74b9ff"

class ErrorMessageCreator:
    @staticmethod
    def show_error(title, message):
        messagebox.showerror(title, message)

def get_user_info_from_db(username):
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",        # Change if needed
            password="123456",        # Change if needed
            database="studyswap"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        ErrorMessageCreator.show_error("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία σύνδεσης στη βάση: {e}")
        return None

def get_courses_from_db(university_id):
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",        # Change if needed
            password="123456",  # Change if needed
            database="studyswap"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM course WHERE university_id = %s", (university_id,))
        courses = [row["name"] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return courses
    except Exception as e:
        ErrorMessageCreator.show_error("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία λήψης μαθημάτων: {e}")
        return []

class HomePage(tk.Tk):
    def __init__(self, logged_in_username=None):
        super().__init__()
        self.title("Αρχική Σελίδα")
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        self.configure(bg=BG_COLOR)
        self.geometry("420x540")
        self.current_frame = None
        self.logo_img = None
        self.logged_in_user = None
        if logged_in_username:
            self.logged_in_user = get_user_info_from_db(logged_in_username)
        self.button_style = {
            "font": ("Helvetica", 12, "bold"),
            "bg": PRIMARY_COLOR,
            "fg": "white",
            "activebackground": PRIMARY_ACTIVE,
            "activeforeground": "white",
            "bd": 0,
            "highlightthickness": 0,
            "relief": "flat",
            "cursor": "hand2"
        }
        self.rounded_button_style = {
            "font": ("Helvetica", 12, "bold"),
            "bg": PRIMARY_COLOR,
            "fg": "white",
            "activebackground": PRIMARY_ACTIVE,
            "activeforeground": "white",
            "bd": 0,
            "highlightthickness": 0,
            "relief": "flat",
            "cursor": "hand2",
            "width": 30,
            "height": 2
        }
        self.show_home()

    def make_rounded_button(self, parent, **kwargs):
        btn = tk.Button(parent, **self.rounded_button_style, **kwargs)
        btn.configure(
            padx=10, pady=5
        )
        return btn

    def show_home(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainMenuPage(self, self.logged_in_user)
        self.current_frame.pack(expand=True, fill="both")

    def show_choose_course(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ChooseCoursePage(self, self.logged_in_user)
        self.current_frame.pack(expand=True, fill="both")

    def show_choose_parameters(self, chosen_course):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ChooseParametersPage(self, chosen_course, self.logged_in_user)
        self.current_frame.pack(expand=True, fill="both")

    def show_invite_users(self, group_parameters):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = InviteUsersPage(self, group_parameters, self.logged_in_user)
        self.current_frame.pack(expand=True, fill="both")

    def show_study_group_creator_page(self, group_parameters, invited_users):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StudyGroupCreatorPage(
            self,
            group_parameters["course"],
            group_parameters,
            invited_users,
            on_confirm=self.show_home,
            on_cancel=self.show_home,
            logged_in_user=self.logged_in_user
        )
        self.current_frame.pack(expand=True, fill="both")

class MainMenuPage(tk.Frame):
    def __init__(self, master, logged_in_user=None):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.logged_in_user = logged_in_user

        # Add logo at the top
        logo_path = os.path.join(os.path.dirname(__file__), "StudySwap_logo.png")
        try:
            img = Image.open(logo_path)
            img = img.resize((220, 80), Image.LANCZOS)
            self.master.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(self, image=self.master.logo_img, bg=BG_COLOR)
            logo_label.pack(pady=(18, 10))
        except Exception as e:
            logo_label = tk.Label(self, text="StudySwap", font=("Helvetica", 20, "bold"), bg=BG_COLOR, fg=PRIMARY_COLOR)
            logo_label.pack(pady=(18, 10))

        button_labels = [
            ("Δημιουργία Ομάδας Μελέτης", self.master.show_choose_course),
            ("Αναζήτηση Ομάδας Μελέτης", None),
            ("Επεξεργασία Προφίλ", None),
            ("Συνδρομή", None),
            ("Ρυθμίσεις", None)
        ]

        for label, command in button_labels:
            button = self.master.make_rounded_button(
                self,
                text=label,
                command=command
            ) if command else self.master.make_rounded_button(self, text=label)
            button.pack(pady=12)

        # Optionally show logged-in user at the top right
        if self.logged_in_user:
            user_label = tk.Label(
                self,
                text=f"Συνδεδεμένος ως: {self.logged_in_user.get('name', '')} {self.logged_in_user.get('lastname', '')}",
                font=("Helvetica", 10),
                bg=BG_COLOR,
                fg=PRIMARY_COLOR,
                anchor="e"
            )
            user_label.pack(anchor="ne", padx=10, pady=(5, 0))

class ChooseCoursePage(tk.Frame):
    def __init__(self, master, logged_in_user=None):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.logged_in_user = logged_in_user

        label = tk.Label(self, text="Επιλέξτε Μάθημα:", font=("Helvetica", 15, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        label.pack(pady=24)

        # Get courses from DB for the user's university (now handled inside the class)
        courses = self.get_courses()
        self.selected_course = tk.StringVar(value=courses[0])
        dropdown = tk.OptionMenu(self, self.selected_course, *courses)
        dropdown.config(font=("Helvetica", 12), width=25, bg=INPUT_BG, fg=INPUT_FG, bd=0, highlightthickness=0, relief="flat", activebackground=INPUT_BG)
        dropdown["menu"].config(font=("Helvetica", 12), bg=INPUT_BG, fg=INPUT_FG)
        dropdown.pack(pady=10)

        button_frame = tk.Frame(self, bg=BG_COLOR)
        button_frame.pack(pady=36)

        cancel_btn = tk.Button(
            button_frame,
            text="Ακυρο",
            font=("Helvetica", 12, "bold"),
            bg=SECONDARY_COLOR,
            fg="white",
            activebackground=SECONDARY_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.master.show_home
        )
        cancel_btn.pack(side="left", padx=14)

        confirm_btn = tk.Button(
            button_frame,
            text="Επιβεβαίωση",
            font=("Helvetica", 12, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            activebackground=SUCCESS_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.confirm_course
        )
        confirm_btn.pack(side="left", padx=14)

    def get_courses(self):
        courses = ["Επιλέξτε Μάθημα"]
        if self.logged_in_user and self.logged_in_user.get("university_id"):
            try:
                conn = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",        # Change if needed
                    password="123456",  # Change if needed
                    database="studyswap"
                )
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT name FROM course WHERE university_id = %s", (self.logged_in_user["university_id"],))
                db_courses = [row["name"] for row in cursor.fetchall()]
                cursor.close()
                conn.close()
                courses.extend(db_courses)
            except Exception as e:
                ErrorMessageCreator.show_error("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία λήψης μαθημάτων: {e}")
        return courses

    def confirm_course(self):
        if self.selected_course.get() == "Επιλέξτε Μάθημα":
            ErrorMessageCreator.show_error("Σφάλμα", "Παρακαλώ επιλέξτε μάθημα πριν συνεχίσετε.")
            return
        self.master.show_choose_parameters(self.selected_course.get())

class ChooseParametersPage(tk.Frame):
    def __init__(self, master, chosen_course, logged_in_user=None):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.chosen_course = chosen_course
        self.logged_in_user = logged_in_user

        label = tk.Label(self, text="Ορίστε Παραμέτρους Ομάδας", font=("Helvetica", 15, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        label.pack(pady=24)

        max_label = tk.Label(self, text="Μέγιστος Αριθμός Ατόμων:", font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR)
        max_label.pack(pady=(10, 0))
        self.max_people = tk.IntVar(value=5)
        max_spinbox = tk.Spinbox(self, from_=2, to=20, textvariable=self.max_people, font=("Helvetica", 12), width=5, bg=INPUT_BG, fg=INPUT_FG, bd=0, relief="flat")
        max_spinbox.pack(pady=5)

        date_label = tk.Label(self, text="Ημερομηνία Διεξαγωγής (π.χ. 2024-06-30):", font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR)
        date_label.pack(pady=(10, 0))
        self.date_entry = tk.Entry(self, font=("Helvetica", 12), width=20, bg=INPUT_BG, fg=INPUT_FG, bd=0, relief="flat")
        self.date_entry.pack(pady=5)

        time_label = tk.Label(self, text="Ώρα Διεξαγωγής (π.χ. 18:00):", font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR)
        time_label.pack(pady=(10, 0))
        self.time_entry = tk.Entry(self, font=("Helvetica", 12), width=20, bg=INPUT_BG, fg=INPUT_FG, bd=0, relief="flat")
        self.time_entry.pack(pady=5)

        button_frame = tk.Frame(self, bg=BG_COLOR)
        button_frame.pack(pady=36)

        cancel_btn = tk.Button(
            button_frame,
            text="Ακυρο",
            font=("Helvetica", 12, "bold"),
            bg=SECONDARY_COLOR,
            fg="white",
            activebackground=SECONDARY_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.master.show_home
        )
        cancel_btn.pack(side="left", padx=14)

        confirm_btn = tk.Button(
            button_frame,
            text="Επιβεβαίωση",
            font=("Helvetica", 12, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            activebackground=SUCCESS_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.confirm_parameters
        )
        confirm_btn.pack(side="left", padx=14)

    def confirm_parameters(self):
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        max_people = self.max_people.get()
        missing = []
        # Validate date format YYYY-MM-DD
        date_valid = False
        try:
            if date:
                datetime.strptime(date, "%Y-%m-%d")
                date_valid = True
        except ValueError:
            date_valid = False

        # Validate time format HH:MM (24h)
        time_valid = False
        if time and re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time):
            time_valid = True

        # Validate max_people is integer and >=2
        try:
            max_people_int = int(max_people)
            max_people_valid = max_people_int >= 2
        except Exception:
            max_people_valid = False

        if not date:
            missing.append("ημερομηνία")
        elif not date_valid:
            ErrorMessageCreator.show_error("Σφάλμα", "Η ημερομηνία πρέπει να είναι στη μορφή YYYY-MM-DD.")
            return

        if not time:
            missing.append("ώρα")
        elif not time_valid:
            ErrorMessageCreator.show_error("Σφάλμα", "Η ώρα πρέπει να είναι στη μορφή HH:MM (24ωρη).")
            return

        if not str(max_people):
            missing.append("μέγιστος αριθμός ατόμων")
        elif not max_people_valid:
            ErrorMessageCreator.show_error("Σφάλμα", "Ο μέγιστος αριθμός ατόμων πρέπει να είναι ακέραιος >= 2.")
            return

        if missing:
            ErrorMessageCreator.show_error("Σφάλμα", "Παρακαλώ συμπληρώστε: " + ", ".join(missing) + ".")
            return

        group_parameters = {
            "course": self.chosen_course,
            "max_people": max_people,
            "date": date,
            "time": time
        }
        self.master.show_invite_users(group_parameters)

class InviteUsersPage(tk.Frame):
    def __init__(self, master, group_parameters, logged_in_user=None):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.group_parameters = group_parameters
        self.invited_users = []
        self.logged_in_user = logged_in_user
        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="Προσκαλέστε Χρήστες", font=("Helvetica", 15, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        label.pack(pady=24)

        entry_frame = tk.Frame(self, bg=BG_COLOR)
        entry_frame.pack(pady=10)

        entry_label = tk.Label(entry_frame, text="Όνομα χρήστη:", font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR)
        entry_label.pack(side="left", padx=(0, 8))

        self.username_entry = tk.Entry(entry_frame, font=("Helvetica", 12), width=18, bg=INPUT_BG, fg=INPUT_FG, bd=0, relief="flat")
        self.username_entry.pack(side="left")

        add_btn = tk.Button(
            entry_frame,
            text="Προσθήκη",
            font=("Helvetica", 12, "bold"),
            bg=ADD_BTN_COLOR,
            fg="white",
            activebackground=ADD_BTN_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            command=self.add_user_to_list
        )
        add_btn.pack(side="left", padx=(8, 0))

        self.users_listbox = tk.Listbox(self, font=("Helvetica", 12), width=30, height=6, bg=INPUT_BG, fg=INPUT_FG, bd=0, relief="flat")
        self.users_listbox.pack(pady=16)

        button_frame = tk.Frame(self, bg=BG_COLOR)
        button_frame.pack(pady=24)

        cancel_btn = tk.Button(
            button_frame,
            text="Ακυρο",
            font=("Helvetica", 12, "bold"),
            bg=SECONDARY_COLOR,
            fg="white",
            activebackground=SECONDARY_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.master.show_home
        )
        cancel_btn.pack(side="left", padx=10)

        skip_btn = tk.Button(
            button_frame,
            text="Παράλειψη",
            font=("Helvetica", 12, "bold"),
            bg=WARNING_COLOR,
            fg="white",
            activebackground=WARNING_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.skip_invites
        )
        skip_btn.pack(side="left", padx=10)

        confirm_btn = tk.Button(
            button_frame,
            text="Επιβεβαίωση",
            font=("Helvetica", 12, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            activebackground=SUCCESS_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.confirm_invites
        )
        confirm_btn.pack(side="left", padx=10)

    def add_user_to_list(self):
        username = self.username_entry.get().strip()
        if username and username not in self.invited_users:
            self.invited_users.append(username)
            self.users_listbox.insert(tk.END, username)
            self.username_entry.delete(0, tk.END)
        elif not username:
            ErrorMessageCreator.show_error("Σφάλμα", "Παρακαλώ εισάγετε όνομα χρήστη.")
        else:
            ErrorMessageCreator.show_error("Σφάλμα", "Ο χρήστης έχει ήδη προστεθεί.")

    def user_exists_in_db(self, username):
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",        # Change if needed
                password="123456",  # Change if needed
                database="studyswap"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user WHERE username = %s", (username,))
            exists = cursor.fetchone()[0] > 0
            cursor.close()
            conn.close()
            return exists
        except Exception as e:
            ErrorMessageCreator.show_error("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία ελέγχου χρήστη: {e}")
            return False

    def confirm_invites(self):
        if not self.invited_users:
            ErrorMessageCreator.show_error("Σφάλμα", "Παρακαλώ προσθέστε τουλάχιστον έναν χρήστη για πρόσκληση.")
            return
        # Check if all users exist in the database
        not_found = []
        for username in self.invited_users:
            if not self.user_exists_in_db(username):
                not_found.append(username)
        if not_found:
            ErrorMessageCreator.show_error(
                "Σφάλμα",
                "Οι παρακάτω χρήστες δεν βρέθηκαν στη βάση δεδομένων: " + ", ".join(not_found)
            )
            return
        self.master.show_study_group_creator_page(self.group_parameters, self.invited_users)

    def skip_invites(self):
        self.invited_users = []
        self.master.show_study_group_creator_page(self.group_parameters, self.invited_users)

class StudyGroupCreatorPage(tk.Frame):
    def __init__(self, parent, course, parameters, users, on_confirm, on_cancel, logged_in_user=None):
        super().__init__(parent, bg=BG_COLOR)
        self.parent = parent
        self.course = course
        self.parameters = parameters
        self.users = users
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.logged_in_user = logged_in_user
        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="Επιβεβαίωση Δημιουργίας Ομάδας", font=("Helvetica", 15, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        label.pack(pady=24)

        info = (
            f"Μάθημα: {self.course}\n"
            f"Μέγιστος Αριθμός Ατόμων: {self.parameters['max_people']}\n"
            f"Ημερομηνία: {self.parameters['date']}\n"
            f"Ώρα: {self.parameters['time']}\n"
            f"Προσκαλούμενοι: {', '.join(self.users) if self.users else 'Κανένας'}"
        )
        info_label = tk.Label(self, text=info, font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR, justify="left")
        info_label.pack(pady=16)

        button_frame = tk.Frame(self, bg=BG_COLOR)
        button_frame.pack(pady=24)

        cancel_btn = tk.Button(
            button_frame,
            text="Ακυρο",
            font=("Helvetica", 12, "bold"),
            bg=SECONDARY_COLOR,
            fg="white",
            activebackground=SECONDARY_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.on_cancel
        )
        cancel_btn.pack(side="left", padx=14)

        confirm_btn = tk.Button(
            button_frame,
            text="Επιβεβαίωση",
            font=("Helvetica", 12, "bold"),
            bg=SUCCESS_COLOR,
            fg="white",
            activebackground=SUCCESS_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.create_study_group
        )
        confirm_btn.pack(side="left", padx=14)

    def create_study_group(self):
        # Insert the study group into the database
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",        # Change if needed
                password="123456",  # Change if needed
                database="studyswap"
            )
            cursor = conn.cursor(dictionary=True)

            # Get course_id for the selected course name and university
            cursor.execute(
                "SELECT id FROM course WHERE name = %s AND university_id = %s",
                (self.course, self.logged_in_user["university_id"])
            )
            course_row = cursor.fetchone()
            if not course_row:
                ErrorMessageCreator.show_error("Σφάλμα", "Το μάθημα δεν βρέθηκε στη βάση δεδομένων.")
                cursor.close()
                conn.close()
                return
            course_id = course_row["id"]

            # Insert study group
            cursor.execute(
                "INSERT INTO studygroup (course_id, creator_id, max_members, date, time) VALUES (%s, %s, %s, %s, %s)",
                (
                    course_id,
                    self.logged_in_user["id"],
                    int(self.parameters["max_people"]),
                    self.parameters["date"],
                    self.parameters["time"]
                )
            )
            studygroup_id = cursor.lastrowid

            # Add creator as a member (status 'accepted')
            cursor.execute(
                "INSERT INTO studygroup_member (studygroup_id, user_id, status) VALUES (%s, %s, %s)",
                (studygroup_id, self.logged_in_user["id"], "accepted")
            )

            # Add invited users as 'invited'
            for username in self.users:
                cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
                user_row = cursor.fetchone()
                if user_row:
                    cursor.execute(
                        "INSERT INTO studygroup_member (studygroup_id, user_id, status) VALUES (%s, %s, %s)",
                        (studygroup_id, user_row["id"], "invited")
                    )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Επιτυχία", "Η ομάδα μελέτης δημιουργήθηκε επιτυχώς!")
            self.on_confirm()
        except Exception as e:
            ErrorMessageCreator.show_error("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία δημιουργίας ομάδας: {e}")

if __name__ == "__main__":
    # Simulate a logged-in user by setting the username here.
    # To test with a different user, just change the username below.
    logged_in_username = "user1"  # <-- Change this to test with another user
    app = HomePage(logged_in_username=logged_in_username)
    app.mainloop()