# Αντικειμενοστραφής μετατροπή του Use Case 4: Συνδρομητική Υπηρεσία
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, timedelta

CURRENT_USER_ID = None
CURRENT_USERNAME = None
SUBSCRIPTION_COST = 6.99

# --- Βοηθητικές Κλάσεις ---
class Database:
    def __init__(self, db_name="study_platform.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def checkLoginStatus(self, email, password):
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, first_name FROM Users WHERE email=? AND password=?", (email, password))
            return cur.fetchone()

    def userHasActiveSubscription(self, user_id):
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM Subscriptions
                WHERE user_id=? AND is_active=1 AND end_date >= DATE('now')
            """, (user_id,))
            return cur.fetchone() is not None

    def insertSubscription(self, user_id, sub_type):
        with self.connect() as conn:
            cur = conn.cursor()
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

            cur.execute("""
                INSERT INTO Payments (user_id, amount, status, date)
                VALUES (?, ?, ?, ?)
            """, (user_id, SUBSCRIPTION_COST, 'success', start_date))

            cur.execute("""
                INSERT INTO Subscriptions (user_id, type, is_active, start_date, end_date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, sub_type, 1, start_date, end_date))

            conn.commit()

# --- Κύρια Κλάση Διαχείρισης Συνδρομής ---
class SubscriptionManager:
    def __init__(self, root):
        self.root = root
        self.db = Database()

    def navigateToSubscription(self):
        if not self.checkLoginStatus():
            self.displayLoginPrompt()
        else:
            self.displayPlans()

    def checkLoginStatus(self):
        return CURRENT_USER_ID is not None

    def displayLoginPrompt(self):
        def attempt_login():
            global CURRENT_USER_ID, CURRENT_USERNAME
            result = self.db.checkLoginStatus(email_entry.get(), password_entry.get())
            if result:
                CURRENT_USER_ID, CURRENT_USERNAME = result
                messagebox.showinfo("Επιτυχία", f"Καλωσήρθες, {CURRENT_USERNAME}!")
                login.destroy()
                self.displayPlans()
            else:
                messagebox.showerror("Σφάλμα", "Λάθος email ή κωδικός")

        login = tk.Toplevel(self.root)
        login.title("Σύνδεση")
        login.geometry("300x200")

        tk.Label(login, text="Email:").pack(pady=5)
        email_entry = tk.Entry(login)
        email_entry.pack()

        tk.Label(login, text="Κωδικός:").pack(pady=5)
        password_entry = tk.Entry(login, show="*")
        password_entry.pack()

        tk.Button(login, text="Σύνδεση", command=attempt_login).pack(pady=15)

    def displayPlans(self):
        window = tk.Toplevel(self.root)
        window.title("Συνδρομητικά Πλάνα")
        window.geometry("700x450")
        window.configure(bg="#f4f4f4")

        ttk.Label(window, text=f"Καλωσήρθες, {CURRENT_USERNAME}", font=("Segoe UI", 12, "italic")).pack(pady=(10, 0))
        ttk.Label(window, text="Επέλεξε Συνδρομή", font=("Segoe UI", 16, "bold")).pack(pady=10)

        frame = ttk.Frame(window, padding=15)
        frame.pack(pady=10, fill="both", expand=True)

        for i, sub_type in enumerate(["Φοιτητής", "Φοιτητής-Διδάσκων"]):
            features = [
                "• Χωρίς διαφημίσεις", "• Premium ομάδες", "• Σημειώσεις", "• Μαθήματα"
            ] if sub_type == "Φοιτητής" else [
                "• Προβολή", "• Εργαλεία", "• Μαθήματα", "• Premium"
            ]

            group = ttk.LabelFrame(frame, text=sub_type, padding=10)
            group.grid(row=0, column=i, padx=20, sticky="n")
            ttk.Label(group, text="6.99€/μήνα", font=("Segoe UI", 11, "bold")).pack()
            ttk.Label(group, text="\n".join(features), justify="left").pack()
            ttk.Button(group, text="Επιλογή", command=lambda st=sub_type: self.proceedToPayment(st)).pack(pady=10)

    def proceedToPayment(self, subscriptionType):
        PaymentPage(self.root, subscriptionType, self.db)

# --- Κλάση Φόρμας Πληρωμής ---
class PaymentPage:
    def __init__(self, root, subscriptionType, db):
        self.root = root
        self.subscriptionType = subscriptionType
        self.db = db
        self.display()

    def display(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Πληρωμή")
        self.window.geometry("350x330")

        tk.Label(self.window, text="Αριθμός Κάρτας:").pack()
        self.card_number_entry = tk.Entry(self.window)
        self.card_number_entry.pack()
        self.card_number_error = tk.Label(self.window, text="", fg="red")
        self.card_number_error.pack()

        tk.Label(self.window, text="Όνομα Κατόχου:").pack()
        self.card_name_entry = tk.Entry(self.window)
        self.card_name_entry.pack()
        self.card_name_error = tk.Label(self.window, text="", fg="red")
        self.card_name_error.pack()

        tk.Label(self.window, text="Ημερομηνία Λήξης (MM/YY):").pack()
        self.expiry_var = tk.StringVar()
        self.expiry_entry = tk.Entry(self.window, textvariable=self.expiry_var)
        self.expiry_entry.pack()
        self.expiry_entry.bind("<KeyRelease>", self.format_expiry)
        self.expiry_error = tk.Label(self.window, text="", fg="red")
        self.expiry_error.pack()

        tk.Label(self.window, text="CVV:").pack()
        self.cvv_entry = tk.Entry(self.window, show="*")
        self.cvv_entry.pack()

        tk.Button(self.window, text=f"Πληρωμή {SUBSCRIPTION_COST:.2f}€", command=self.validate_and_submit).pack(pady=10)

    def format_expiry(self, event):
        value = self.expiry_var.get().replace("/", "")[:4]
        if len(value) > 2:
            value = value[:2] + "/" + value[2:]
        self.expiry_var.set(value)

    def validate_and_submit(self):
        valid = True
        for entry, label in [
            (self.card_number_entry, self.card_number_error),
            (self.expiry_entry, self.expiry_error),
            (self.card_name_entry, self.card_name_error)
        ]:
            entry.config(highlightbackground="gray", highlightthickness=1)
            label.config(text="")

        card_number = self.card_number_entry.get()
        if not card_number.isdigit():
            self.card_number_entry.config(highlightbackground="red", highlightthickness=2)
            self.card_number_error.config(text="Μόνο αριθμοί επιτρέπονται")
            valid = False
        elif len(card_number) != 16:
            self.card_number_entry.config(highlightbackground="red", highlightthickness=2)
            self.card_number_error.config(text="Ο αριθμός πρέπει να περιέχει 16 ψηφία")
            valid = False

        expiry = self.expiry_var.get()
        if len(expiry) != 5 or expiry[2] != "/" or not expiry.replace("/", "").isdigit():
            self.expiry_entry.config(highlightbackground="red", highlightthickness=2)
            self.expiry_error.config(text="Μορφή: MM/YY")
            valid = False

        card_name = self.card_name_entry.get()
        if not all(ord(c) < 128 for c in card_name):
            self.card_name_entry.config(highlightbackground="red", highlightthickness=2)
            self.card_name_error.config(text="Μόνο λατινικοί χαρακτήρες")
            valid = False

        if valid:
            if self.db.userHasActiveSubscription(CURRENT_USER_ID):
                messagebox.showinfo("Πληροφορία", "Έχετε ήδη ενεργή συνδρομή.")
            else:
                self.db.insertSubscription(CURRENT_USER_ID, self.subscriptionType)
            self.window.destroy()


# --- Εκκίνηση Εφαρμογής ---
if __name__ == "__main__":
    app = tk.Tk()
    app.title("Συνδρομές")
    app.geometry("300x200")

    manager = SubscriptionManager(app)

    tk.Label(app, text="Καλώς ήρθατε στην εφαρμογή!", font=("Segoe UI", 12, "bold")).pack(pady=20)
    tk.Button(app, text="Διαχείριση Συνδρομής", command=manager.navigateToSubscription).pack(pady=10)

    app.mainloop()
