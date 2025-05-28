import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import re
import os
from database import Student, session, hash_password

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@(?:gmail|yahoo)\.com$", email)

# GUI
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Platform - Login/Register")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f4ff")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Replace image loading with unicode characters
        self.eye_open = "👁"  # Unicode eye symbol
        self.eye_closed = "🔒"  # Unicode lock symbol
        
        # Initialize password buttons dictionary
        self.show_password_buttons = {}
        
        # Create login screen
        self.create_login_screen()

    def toggle_password_visibility(self, entry):
        """Toggle password visibility for the given entry"""
        if entry['show'] == '*':
            entry.config(show='')
            return True  # is_visible
        else:
            entry.config(show='*')
            return False  # is_hidden

    def create_password_field(self, parent, row, column, label):
        """Create a password field with a show/hide button"""
        frame = tk.Frame(parent, bg="#f0f4ff")
        frame.grid(row=row, column=column, pady=3, padx=10, sticky="w")

        # Create password entry
        entry = tk.Entry(frame, font=("Arial", 12), width=30, show="*")
        entry.pack(side=tk.LEFT)

        # Create toggle button with unicode character
        show_btn = tk.Button(frame, text=self.eye_closed, font=("Arial", 12), bd=0, 
                            bg="#f0f4ff", command=lambda: self.update_password_button(show_btn, entry))
        show_btn.pack(side=tk.LEFT, padx=5)
    
        return entry

    def update_password_button(self, button, entry):
        """Update the button text based on password visibility"""
        is_visible = self.toggle_password_visibility(entry)
        button.config(text=self.eye_open if is_visible else self.eye_closed)

    def create_error_label(self, parent, row, column):
        error_label = tk.Label(parent, text="", fg="red", bg="#f0f4ff", font=("Arial", 10))
        error_label.grid(row=row, column=column, sticky="w", padx=10)
        return error_label

    def create_login_screen(self):
        self.clear_screen()
        self.login_error_labels = {}

        # Title
        tk.Label(self.root, text="StudySwap", font=("Arial", 24, "bold"), fg="blue", bg="#f0f4ff").grid(row=0, column=0, columnspan=2, pady=20)
        
        # Create frame for email input
        email_frame = tk.Frame(self.root, bg="#f0f4ff")
        email_frame.grid(row=1, column=1, pady=3, padx=10, sticky="w")
        
        # Email field
        tk.Label(self.root, text="Email:", font=("Arial", 12), bg="#f0f4ff").grid(row=1, column=0, pady=5, sticky="e")
        self.email_entry = tk.Entry(email_frame, font=("Arial", 12), width=30)
        self.email_entry.pack(side=tk.LEFT)
        self.login_error_labels["Email"] = self.create_error_label(self.root, 2, 1)

        # Password field
        tk.Label(self.root, text="Κωδικός:", font=("Arial", 12), bg="#f0f4ff").grid(row=3, column=0, pady=5, sticky="e")
        self.pass_entry = self.create_password_field(self.root, 3, 1, "Κωδικός")
        self.login_error_labels["Password"] = self.create_error_label(self.root, 4, 1)

        # Buttons
        tk.Button(self.root, text="Σύνδεση", font=("Arial", 12), bg="lightblue", 
              command=self.login).grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Εγγραφή", font=("Arial", 12), bg="lightblue", 
              command=self.create_register_screen).grid(row=6, column=0, columnspan=2)

    def create_register_screen(self):
        self.clear_screen()
        fields = ["Όνομα", "Επώνυμο", "Email", "Σχολή", "Κωδικός"]
        self.reg_entries = {}
        self.reg_error_labels = {}

        tk.Label(self.root, text="Εγγραφή Χρήστη", font=("Arial", 20, "bold"), fg="blue", bg="#f0f4ff").grid(row=0, column=0, columnspan=2, pady=20)

        for i, label in enumerate(fields):
            # Label
            tk.Label(self.root, text=label + ":", font=("Arial", 12), bg="#f0f4ff").grid(row=i*2+1, column=0, sticky="e", pady=5)
            
            # Create frame for input field
            input_frame = tk.Frame(self.root, bg="#f0f4ff")
            input_frame.grid(row=i*2+1, column=1, pady=5, padx=10, sticky="w")
            
            if label == "Κωδικός":
                # Use the password field creator method
                entry = self.create_password_field(input_frame, i*2+1, 1, label)
            else:
                # Regular entry field
                entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
                entry.pack(side=tk.LEFT)
            
            self.reg_entries[label] = entry
            self.reg_error_labels[label] = self.create_error_label(self.root, i*2+2, 1)

        # Create button frame for better button organization
        button_frame = tk.Frame(self.root, bg="#f0f4ff")
        button_frame.grid(row=len(fields)*2+1, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Εγγραφή", font=("Arial", 12), bg="lightblue", 
                  command=self.register).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Πίσω", font=("Arial", 12), bg="lightblue", 
                  command=self.create_login_screen).pack(side=tk.LEFT, padx=5)

    def create_main_screen(self, student):
        self.clear_screen()
        self.student = student

        tk.Label(self.root, text=f"Καλωσήρθες, {student.name} {student.surname}", font=("Arial", 20), fg="blue", bg="#f0f4ff").pack(pady=20)
        tk.Button(self.root, text="Προβολή Προφίλ", font=("Arial", 12), bg="lightblue", command=self.create_profile_screen).pack(pady=5)
        tk.Button(self.root, text="Αποσύνδεση", font=("Arial", 12), bg="lightblue", command=self.create_login_screen).pack(pady=5)

    def create_profile_screen(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Προφίλ: {self.student.name} {self.student.surname}", font=("Arial", 18), fg="blue", bg="#f0f4ff").grid(row=0, column=0, columnspan=2, pady=20)

        info = [
            ("Email", self.student.email),
            ("Σχολή", self.student.school),
            ("Τηλέφωνο", self.student.phone),
            ("Bio", self.student.bio)
        ]
        for i, (label, value) in enumerate(info):
            tk.Label(self.root, text=label + ":", font=("Arial", 12), bg="#f0f4ff").grid(row=i+1, column=0, sticky="e", pady=2)
            tk.Label(self.root, text=value, font=("Arial", 12), bg="#f0f4ff").grid(row=i+1, column=1, sticky="w", pady=2)

        tk.Button(self.root, text="Επεξεργασία Προφίλ", font=("Arial", 12), bg="lightblue", command=self.create_profile_edit_screen).grid(row=len(info)+1, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Πίσω", font=("Arial", 12), bg="lightblue", command=lambda: self.create_main_screen(self.student)).grid(row=len(info)+2, column=0, columnspan=2)

    def create_profile_edit_screen(self):
        self.clear_screen()
        self.profile_fields = {}
        self.profile_error_labels = {}
        # Store original values for cancel operation
        self.original_values = {
            "Όνομα": self.student.name,
            "Επώνυμο": self.student.surname,
            "Email": self.student.email,
            "Σχολή": self.student.school,
            "Τηλέφωνο": self.student.phone,
            "Bio": self.student.bio
        }

        tk.Label(self.root, text="Επεξεργασία Προφίλ", font=("Arial", 18), fg="blue", bg="#f0f4ff").grid(row=0, column=0, columnspan=2, pady=20)
        fields = [
            ("Όνομα", self.student.name),
            ("Επώνυμο", self.student.surname),
            ("Email", self.student.email),
            ("Σχολή", self.student.school),
            ("Τηλέφωνο", self.student.phone),
            ("Bio", self.student.bio),
            ("Τρέχων Κωδικός", ""),
            ("Νέος Κωδικός", ""),
            ("Επιβεβαίωση Κωδικού", "")
        ]
        
        for i, (label, value) in enumerate(fields):
            # Label
            tk.Label(self.root, text=label + ":", font=("Arial", 12), bg="#f0f4ff").grid(row=i*2+1, column=0, pady=3, sticky="e")
            
            # Create frame for input field
            input_frame = tk.Frame(self.root, bg="#f0f4ff")
            input_frame.grid(row=i*2+1, column=1, pady=3, padx=10, sticky="w")
            
            password_fields = ["Τρέχων Κωδικός", "Νέος Κωδικός", "Επιβεβαίωση Κωδικού"]
            
            if label in password_fields:
                # Password field with show/hide button
                entry = tk.Entry(input_frame, font=("Arial", 12), width=30, show="*")
                entry.pack(side=tk.LEFT)
                
                # Add show/hide button
                show_btn = tk.Button(input_frame, text=self.eye_closed, font=("Arial", 12), bd=0,
                                   bg="#f0f4ff", command=lambda e=entry, b=None: self.update_password_button(b, e))
                show_btn.pack(side=tk.LEFT, padx=5)
                # Update the button reference after it's created
                show_btn.configure(command=lambda e=entry, b=show_btn: self.update_password_button(b, e))
            else:
                # Regular entry field
                entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
                entry.pack(side=tk.LEFT)
                if value:
                    entry.insert(0, value)
            
            self.profile_fields[label] = entry
            self.profile_error_labels[label] = self.create_error_label(self.root, i*2+2, 1)

        # Create button frame for better button organization
        button_frame = tk.Frame(self.root, bg="#f0f4ff")
        button_frame.grid(row=len(fields)*2+1, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Αποθήκευση", font=("Arial", 12), bg="lightblue", 
                  command=self.update_profile).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Ακύρωση", font=("Arial", 12), bg="lightblue", 
                  command=self.cancel_profile_edit).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Πίσω", font=("Arial", 12), bg="lightblue", 
                  command=self.create_profile_screen).pack(side=tk.LEFT, padx=5)

    def cancel_profile_edit(self):
        if messagebox.askyesno("Επιβεβαίωση", "Είστε σίγουροι ότι θέλετε να ακυρώσετε τις αλλαγές?"):
            # Reset all fields except password fields to original values
            for field, value in self.original_values.items():
                if field in self.profile_fields:
                    self.profile_fields[field].delete(0, tk.END)
                    self.profile_fields[field].insert(0, value)
            
            # Clear password fields
            self.profile_fields["Νέος Κωδικός"].delete(0, tk.END)
            self.profile_fields["Επιβεβαίωση Κωδικού"].delete(0, tk.END)
            
            # Clear error messages
            for label in self.profile_error_labels.values():
                label.config(text="")

    def register(self):
        for label in self.reg_error_labels.values():
            label.config(text="")

        name = self.reg_entries["Όνομα"].get()
        surname = self.reg_entries["Επώνυμο"].get()
        email = self.reg_entries["Email"].get()
        school = self.reg_entries["Σχολή"].get()
        password = self.reg_entries["Κωδικός"].get()

        has_error = False
        if not name:
            self.reg_error_labels["Όνομα"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True
        if not surname:
            self.reg_error_labels["Επώνυμο"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True
        if not email:
            self.reg_error_labels["Email"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True
        elif not is_valid_email(email):
            self.reg_error_labels["Email"].config(text="Το email δεν είναι έγκυρο")
            has_error = True
        if not school:
            self.reg_error_labels["Σχολή"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True
        if not password:
            self.reg_error_labels["Κωδικός"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True

        if has_error:
            return

        if session.query(Student).filter_by(email=email).first():
            self.reg_error_labels["Email"].config(text="Το email χρησιμοποιείται ήδη")
            return

        # Add confirmation dialog
        if messagebox.askyesno("Επιβεβαίωση", "Είστε σίγουροι ότι θέλετε να ολοκληρώσετε την εγγραφή?"):
            student = Student(
                name=name, surname=surname, email=email,
                school=school, password_hash=hash_password(password)
            )
            session.add(student)
            session.commit()
            self.create_main_screen(student)

    def login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()

        if not email or not password:
            if not email:
                self.login_error_labels["Email"].config(text="Το πεδίο είναι υποχρεωτικό")
            if not password:
                self.login_error_labels["Password"].config(text="Το πεδίο είναι υποχρεωτικό")
            return

        student = session.query(Student).filter_by(email=email).first()
        if not student or student.password_hash != hash_password(password):
            self.login_error_labels["Email"].config
            self.login_error_labels["Password"].config(text="Λάθος email ή κωδικός")
        else:
            self.create_main_screen(student)

    def update_profile(self):
        for label in self.profile_error_labels.values():
            label.config(text="")

        # Get all field values
        name = self.profile_fields["Όνομα"].get()
        surname = self.profile_fields["Επώνυμο"].get()
        email = self.profile_fields["Email"].get()
        school = self.profile_fields["Σχολή"].get()
        phone = self.profile_fields["Τηλέφωνο"].get()
        bio = self.profile_fields["Bio"].get()
        current_password = self.profile_fields["Τρέχων Κωδικός"].get()
        new_password = self.profile_fields["Νέος Κωδικός"].get()
        confirm_password = self.profile_fields["Επιβεβαίωση Κωδικού"].get()

        has_error = False
        if not name:
            self.profile_error_labels["Όνομα"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True
        if not surname:
            self.profile_error_labels["Επώνυμο"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True
        if not email:
            self.profile_error_labels["Email"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True
        elif not is_valid_email(email):
            self.profile_error_labels["Email"].config(text="Το email δεν είναι έγκυρο")
            has_error = True
        if not school:
            self.profile_error_labels["Σχολή"].config(text="Το πεδίο είναι υποχρεωτικό")
            has_error = True
        if phone and (not phone.isdigit() or len(phone) != 10):
            self.profile_error_labels["Τηλέφωνο"].config(text="Το τηλέφωνο δεν είναι έγκυρο")
            has_error = True
        if len(bio) > 300:
            self.profile_error_labels["Bio"].config(text="Το bio δεν πρέπει να ξεπερνά τους 300 χαρακτήρες")
            has_error = True

        # Password validation
        if new_password or confirm_password:  # If either new password field is filled
            if not current_password:
                self.profile_error_labels["Τρέχων Κωδικός"].config(text="Απαιτείται ο τρέχων κωδικός")
                has_error = True
            elif hash_password(current_password) != self.student.password_hash:
                self.profile_error_labels["Τρέχων Κωδικός"].config(text="Λάθος κωδικός")
                has_error = True
            
            if new_password != confirm_password:
                self.profile_error_labels["Επιβεβαίωση Κωδικού"].config(text="Οι κωδικοί δεν ταιριάζουν")
                has_error = True
            elif len(new_password) < 6:
                self.profile_error_labels["Νέος Κωδικός"].config(text="Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες")
                has_error = True

        if has_error:
            return

        # Add confirmation dialog
        if messagebox.askyesno("Επιβεβαίωση", "Είστε σίγουροι ότι θέλετε να αποθηκεύσετε τις αλλαγές;"):
            self.student.name = name
            self.student.surname = surname
            self.student.email = email
            self.student.school = school
            self.student.phone = phone
            self.student.bio = bio
            
            # Update password if new one was provided
            if new_password:
                self.student.password_hash = hash_password(new_password)
                
            session.commit()
            self.create_profile_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()