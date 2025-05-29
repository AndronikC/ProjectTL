import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import mysql.connector
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Color palette (same as createStudyGroupApp.py)
BG_COLOR = "#fefefe"
PRIMARY_COLOR = "#4078c0"
PRIMARY_ACTIVE = "#5fa8d3"
TEXT_COLOR = "#222f3e"

def get_user_info_from_db(username):
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",        # Change if needed
            password="123456",  # Change if needed
            database="studyswap"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        tk.messagebox.showerror("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία σύνδεσης στη βάση: {e}")
        return None

class ErrorMessageCreator:
    @staticmethod
    def show_error(title, message):
        tk.messagebox.showerror(title, message)

class CodeConfirmationPage(tk.Frame):
    def __init__(self, master, user_id):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.user_id = user_id

        label = tk.Label(
            self,
            text="Εισάγετε τον 6-ψήφιο Κωδικό Επαλήθευσης",
            font=("Helvetica", 14, "bold"),
            bg=BG_COLOR,
            fg=PRIMARY_COLOR
        )
        label.pack(pady=(40, 20))

        self.code_entry = tk.Entry(self, font=("Helvetica", 13), width=10, bg="#f0f0f0", fg=TEXT_COLOR, bd=1, relief="flat", justify="center")
        self.code_entry.pack(pady=(0, 18))

        confirm_btn = tk.Button(
            self,
            text="Επιβεβαίωση",
            font=("Helvetica", 13, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            activebackground=PRIMARY_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=20,
            height=2,
            command=self.confirm_code
        )
        confirm_btn.pack(pady=10)

    def confirm_code(self):
        code = self.code_entry.get().strip()
        if not (code.isdigit() and len(code) == 6):
            ErrorMessageCreator.show_error("Σφάλμα", "Ο κωδικός πρέπει να είναι 6 ψηφία.")
            return
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="123456",
                database="studyswap"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM verification_code WHERE user_id = %s AND code = %s AND is_active = TRUE AND NOW() <= expires_at",
                (self.user_id, code)
            )
            row = cursor.fetchone()
            if row:
                # Optionally, deactivate the code after successful use
                cursor.execute(
                    "UPDATE verification_code SET is_active = FALSE WHERE id = %s",
                    (row["id"],)
                )
                conn.commit()
                tk.messagebox.showinfo("Επιτυχία", "Ο κωδικός επαληθεύτηκε επιτυχώς!")
                # You can proceed to the next step/page here
            else:
                ErrorMessageCreator.show_error("Σφάλμα", "Ο κωδικός δεν είναι έγκυρος ή έχει λήξει.")
            cursor.close()
            conn.close()
        except Exception as e:
            ErrorMessageCreator.show_error("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία ελέγχου κωδικού: {e}")

class AuthenticationPage(tk.Frame):
    def __init__(self, master, logged_in_user=None):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.logged_in_user = logged_in_user

        # Add StudySwap logo at the top
        logo_path = os.path.join(os.path.dirname(__file__), "StudySwap_logo.png")
        try:
            img = Image.open(logo_path)
            img = img.resize((220, 80), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(self, image=self.logo_img, bg=BG_COLOR)
            logo_label.pack(pady=(18, 10))
        except Exception:
            logo_label = tk.Label(self, text="StudySwap", font=("Helvetica", 20, "bold"), bg=BG_COLOR, fg=PRIMARY_COLOR)
            logo_label.pack(pady=(18, 10))

        label = tk.Label(
            self,
            text="Εισάγετε Αριθμό Ακαδημαϊκής Ταυτότητας",
            font=("Helvetica", 14, "bold"),
            bg=BG_COLOR,
            fg=PRIMARY_COLOR
        )
        label.pack(pady=(10, 30))

        self.id_entry = tk.Entry(self, font=("Helvetica", 13), width=22, bg="#f0f0f0", fg=TEXT_COLOR, bd=1, relief="flat", justify="center")
        self.id_entry.pack(pady=(0, 18))

        confirm_btn = tk.Button(
            self,
            text="Επιβεβαίωση",
            font=("Helvetica", 13, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            activebackground=PRIMARY_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=20,
            height=2,
            command=self.confirm_id
        )
        confirm_btn.pack(pady=10)

        # Συνδεδεμένος ως under the button
        if self.logged_in_user:
            user_label = tk.Label(
                self,
                text=f"Συνδεδεμένος ως: {self.logged_in_user.get('name', '')} {self.logged_in_user.get('lastname', '')}",
                font=("Helvetica", 10),
                bg=BG_COLOR,
                fg=PRIMARY_COLOR,
                anchor="center"
            )
            user_label.pack(pady=(15, 0))

    def confirm_id(self):
        academic_id = self.id_entry.get().strip()
        if not (academic_id.isdigit() and len(academic_id) == 10):
            ErrorMessageCreator.show_error("Σφάλμα", "Ο Αριθμός Ακαδημαϊκής Ταυτότητας πρέπει να είναι 10 ψηφία.")
            return

        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",        # Change if needed
                password="123456",  # Change if needed
                database="studyswap"
            )
            cursor = conn.cursor(dictionary=True)
            # Get academic_id info
            cursor.execute(
                "SELECT academic_id.university_id, university.name, academic_id.academic_email FROM academic_id JOIN university ON academic_id.university_id = university.id WHERE academic_id.academic_id_number = %s",
                (academic_id,)
            )
            row = cursor.fetchone()
            if row:
                # Update user table with academic_email, university_id, academic_id_number
                cursor.execute(
                    "UPDATE user SET academic_email = %s, university_id = %s, academic_id_number = %s WHERE id = %s",
                    (row["academic_email"], row["university_id"], academic_id, self.logged_in_user["id"])
                )
                conn.commit()
                # Send verification code to academic email
                EmailHandler.send_verification_code(row["academic_email"])
                # Show code confirmation page
                self.master.current_frame.destroy()
                self.master.current_frame = CodeConfirmationPage(self.master, self.logged_in_user["id"])
                self.master.current_frame.pack(expand=True, fill="both")
            else:
                ErrorMessageCreator.show_error("Σφάλμα", "Ο Αριθμός Ακαδημαϊκής Ταυτότητας δεν βρέθηκε στη βάση δεδομένων.")
            cursor.close()
            conn.close()
        except Exception as e:
            ErrorMessageCreator.show_error("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία ελέγχου/ενημέρωσης Ακαδημαϊκής Ταυτότητας: {e}")

class SuccessRegistrationPage(tk.Tk):
    def __init__(self, logged_in_username=None, on_confirm=None):
        super().__init__()
        self.title("Επιτυχής Εγγραφή")
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        self.configure(bg=BG_COLOR)
        self.geometry("420x300")
        self.on_confirm = on_confirm

        # Simulate logged-in user
        self.logged_in_user = None
        if logged_in_username:
            self.logged_in_user = get_user_info_from_db(logged_in_username)

        self.current_frame = None
        self.show_success_registration()

    def show_success_registration(self):
        if self.current_frame:
            self.current_frame.destroy()

        frame = tk.Frame(self, bg=BG_COLOR)
        self.current_frame = frame
        frame.pack(expand=True, fill="both")

        # Add StudySwap logo at the top
        logo_path = os.path.join(os.path.dirname(__file__), "StudySwap_logo.png")
        try:
            img = Image.open(logo_path)
            img = img.resize((220, 80), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(frame, image=self.logo_img, bg=BG_COLOR)
            logo_label.pack(pady=(18, 10))
        except Exception:
            logo_label = tk.Label(frame, text="StudySwap", font=("Helvetica", 20, "bold"), bg=BG_COLOR, fg=PRIMARY_COLOR)
            logo_label.pack(pady=(18, 10))

        label = tk.Label(
            frame,
            text="Επιτυχής Εγγραφή",
            font=("Helvetica", 18, "bold"),
            bg=BG_COLOR,
            fg=PRIMARY_COLOR
        )
        label.pack(pady=(10, 30))

        confirm_btn = tk.Button(
            frame,
            text="Επιβεβαίωση",
            font=("Helvetica", 13, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            activebackground=PRIMARY_ACTIVE,
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            width=20,
            height=2,
            command=self.show_authentication_page
        )
        confirm_btn.pack(pady=10)

        # Συνδεδεμένος ως under the button
        if self.logged_in_user:
            user_label = tk.Label(
                frame,
                text=f"Συνδεδεμένος ως: {self.logged_in_user.get('name', '')} {self.logged_in_user.get('lastname', '')}",
                font=("Helvetica", 10),
                bg=BG_COLOR,
                fg=PRIMARY_COLOR,
                anchor="center"
            )
            user_label.pack(pady=(15, 0))
    
    def show_authentication_page(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = AuthenticationPage(self, logged_in_user=self.logged_in_user)
        self.current_frame.pack(expand=True, fill="both")

class EmailHandler:
    @staticmethod
    def send_verification_code(academic_email):
        # Generate a 6-digit code
        code = "{:06d}".format(random.randint(0, 999999))
        print(f"[DEBUG] EmailHandler generated code {code} for {academic_email}")

        # Find user_id for this academic_email
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",        # Change if needed
                password="123456",  # Change if needed
                database="studyswap"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM user WHERE academic_email = %s", (academic_email,))
            user_row = cursor.fetchone()
            if not user_row:
                ErrorMessageCreator.show_error("Σφάλμα", "Δεν βρέθηκε χρήστης με αυτό το ακαδημαϊκό email.")
                cursor.close()
                conn.close()
                return None
            user_id = user_row["id"]

            # Insert code into verification_code table
            cursor.execute(
                "INSERT INTO verification_code (user_id, code) VALUES (%s, %s)",
                (user_id, code)
            )
            conn.commit()
            cursor.close()
            conn.close()
            print(f"[DEBUG] Verification code {code} inserted into database for user_id {user_id}")
            return code
        except Exception as e:
            ErrorMessageCreator.show_error("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία αποθήκευσης verification code: {e}")
            return None

if __name__ == "__main__":
    # Simulate a logged-in user by setting the username here.
    # To test with a different user, just change the username below.
    logged_in_username = "user11"  # <-- Change this to test with another user
    app = SuccessRegistrationPage(logged_in_username=logged_in_username)
    app.mainloop()
