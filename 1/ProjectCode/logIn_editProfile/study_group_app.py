import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
from tkcalendar import Calendar
from datetime import datetime

# Dummy user setup
class User:
    def __init__(self, email, subscription=True):
        self.email = email
        self.subscription = subscription
        self.is_teacher = email == "prof@gmail.com"

current_user = None

# Dummy data
study_groups = {
    "Ομάδα 1": {
        "members": ["student@gmail.com", "prof@gmail.com"],
        "notes": ["sample_notes.pdf", "lecture1.pdf"],
        "messages": [
            "prof@gmail.com: Καλώς ήρθατε στην ομάδα!",
            "student@gmail.com: Ευχαριστώ πολύ!"
        ],
        "lessons": [
            ("2025-05-30 18:00", "available"),
            ("2025-05-31 17:00", "available"),
            ("2025-06-01 19:00", "available")
        ],
        "subscriptions_required": []
    }
}

blocked_users = {"Ομάδα 1": ["blocked_student@gmail.com"]}
user_groups = ["Ομάδα 1"]

class JoinStudyGroupPage(tk.Frame):
    def __init__(self, master, current_user, back_callback):
        super().__init__(master)
        self.master = master
        self.current_user = current_user
        self.back_callback = back_callback
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Διαθέσιμες Ομάδες Μελέτης", font=("Arial", 14)).pack(pady=10)
        self.group_listbox = tk.Listbox(self)
        self.group_listbox.pack(pady=5, fill="x", padx=20)
        self.refresh_group_list()

        tk.Button(self, text="Συμμετοχή", command=self.join_group).pack(pady=10)
        tk.Button(self, text="Πίσω", command=self.back_callback).pack()

    def refresh_group_list(self):
        self.group_listbox.delete(0, tk.END)
        for group in study_groups.keys():
            self.group_listbox.insert(tk.END, group)

    def join_group(self):
        selected_index = self.group_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Σφάλμα", "Πρέπει να επιλέξετε ομάδα.")
            return

        group_name = self.group_listbox.get(selected_index)

        if self.current_user.email in study_groups[group_name]["members"]:
            messagebox.showinfo("Πληροφορία", "Είστε ήδη μέλος της ομάδας.")
            return

        study_groups[group_name]["members"].append(self.current_user.email)
        user_groups.append(group_name)
        self.save_data()  # Save after joining group
        messagebox.showinfo("Επιτυχία", f"Εγγραφήκατε στην ομάδα {group_name}.")
        self.back_callback()

class StudyGroupApp(tk.Tk):
    def __init__(self, current_user):
        super().__init__()
        self.title("Πλατφόρμα Ομάδας Μελέτης")
        self.geometry("800x600")
        self.current_user = current_user
        self.group_selected = None
        
        # Load existing notifications
        self.load_notifications()
        
        # Start notification checker
        self.check_notifications_timer = self.after(5000, self.check_notifications)
        
        self.create_group_selection_screen()

    def check_notifications(self):
        """Check for unread notifications"""
        for notif in self.notifications:
            if not notif['read'] and notif['user'] == self.current_user.email:
                messagebox.showinfo("Ειδοποίηση", notif['message'])
                notif['read'] = True
                self.save_notifications()
        
        # Schedule next check
        self.check_notifications_timer = self.after(5000, self.check_notifications)

    def load_data(self):
        """Load data from JSON file"""
        try:
            with open('study_groups_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                global study_groups, blocked_users, user_groups
                study_groups = data['study_groups']
                blocked_users = data['blocked_users']
                user_groups = data['user_groups']
        except FileNotFoundError:
            # If file doesn't exist, use default data
            self.save_data()

    def save_data(self):
        """Save data to JSON file"""
        data = {
            'study_groups': study_groups,
            'blocked_users': blocked_users,
            'user_groups': user_groups
        }
        with open('study_groups_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def on_closing(self):
        """Handler for window closing"""
        if self.check_notifications_timer:
            self.after_cancel(self.check_notifications_timer)
        self.save_data()
        self.destroy()

    def create_group_selection_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        if not user_groups:
            messagebox.showinfo("Καμία ομάδα", "Δεν είστε εγγεγραμμένος σε κάποια ομάδα.")
            return

        tk.Label(self, text="Επιλέξτε ομάδα μελέτης:", font=("Arial", 14)).pack(pady=10)
        self.group_var = tk.StringVar()
        group_dropdown = ttk.Combobox(self, textvariable=self.group_var, values=user_groups)
        group_dropdown.pack(pady=10)

        tk.Button(self, text="Είσοδος", command=self.enter_group).pack()
        tk.Button(self, text="Συμμετοχή σε νέα ομάδα", command=self.show_join_page).pack(pady=5)

    def show_join_page(self):
        for widget in self.winfo_children():
            widget.destroy()
        JoinStudyGroupPage(self, self.current_user, back_callback=self.create_group_selection_screen)

    def enter_group(self):
        group = self.group_var.get()
        if not group:
            messagebox.showerror("Σφάλμα", "Πρέπει να επιλέξετε ομάδα.")
            return

        if self.current_user.email in blocked_users.get(group, []):
            messagebox.showwarning("Απαγόρευση", "Έχετε αποκλειστεί από αυτή την ομάδα.")
            self.create_group_selection_screen()
            return

        self.group_selected = group
        self.create_group_home()

    def create_group_home(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Create header frame for title and logout button
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill="x", pady=10)

        # Add title
        tk.Label(header_frame, text=f"Καλώς ήρθατε στην {self.group_selected}", 
                 font=("Arial", 16)).pack(side=tk.LEFT, padx=20)

        # Add logout button to header
        tk.Button(header_frame, text="Αποσύνδεση", command=self.logout,
                  bg="red", fg="white").pack(side=tk.RIGHT, padx=20)
        
        # Add frame for main buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Σημειώσεις", command=self.notes_section).pack(pady=5)
        tk.Button(button_frame, text="Μηνύματα", command=self.messages_section).pack(pady=5)
        tk.Button(button_frame, text="Μαθήματα", command=self.lessons_section).pack(pady=5)

        if self.current_user.is_teacher:
            tk.Button(button_frame, text="Διαγραφή Ομάδας", command=self.delete_group).pack(pady=5)
            tk.Button(button_frame, text="Προβολή Μελών", command=self.view_members).pack(pady=5)
        
        tk.Button(button_frame, text="Επιστροφή στην Επιλογή Ομάδας", 
                  command=self.create_group_selection_screen).pack(pady=10)

    def logout(self):
        """Handle user logout"""
        if messagebox.askyesno("Αποσύνδεση", "Είστε σίγουροι ότι θέλετε να αποσυνδεθείτε;"):
            self.save_data()  # Save any changes
            self.destroy()
            login_gui()  # Restart login screen

    def messages_section(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text="Μηνύματα", font=("Arial", 14)).pack(pady=10)
        
        # Create message display frame with scrollbar
        msg_frame = tk.Frame(self)
        msg_frame.pack(pady=5, fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(msg_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_box = tk.Text(msg_frame, height=15, width=60, yscrollcommand=scrollbar.set)
        text_box.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=text_box.yview)

        for msg in study_groups[self.group_selected]["messages"]:
            text_box.insert(tk.END, msg + "\n")
        text_box.see(tk.END)  # Auto-scroll to latest message

        entry = tk.Entry(self, width=50)
        entry.pack(pady=5)

        def send_msg():
            msg = f"{self.current_user.email}: {entry.get()}"
            if entry.get().strip():  # Don't send empty messages
                study_groups[self.group_selected]["messages"].append(msg)
                self.save_data()  # Save after sending message
                text_box.insert(tk.END, msg + "\n")
                text_box.see(tk.END)
                entry.delete(0, tk.END)
                
                # Send notifications to other members
                for member in study_groups[self.group_selected]["members"]:
                    if member != self.current_user.email:
                        self.send_notification(member, f"Νέο μήνυμα στην ομάδα {self.group_selected}")

        entry.bind('<Return>', lambda e: send_msg())  # Send on Enter key
        # Create button frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Αποστολή", command=send_msg).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Επιστροφή", 
                  command=self.create_group_home).pack(side=tk.LEFT, padx=5)

    def notes_section(self):
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text="Σημειώσεις", font=("Arial", 14)).pack(pady=10)

        if self.current_user.is_teacher:
            def upload_note():
                file_path = filedialog.askopenfilename(
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
                )
                if file_path:
                    require_subscription = messagebox.askyesno(
                        "Συνδρομή", 
                        "Θέλετε οι σημειώσεις να είναι διαθέσιμες μόνο για συνδρομητές;"
                    )
                    if require_subscription:
                        study_groups[self.group_selected]["subscriptions_required"].append(file_path)
                    study_groups[self.group_selected]["notes"].append(file_path)
                    self.save_data()  # Save after uploading note
                    messagebox.showinfo("Επιτυχία", "Το αρχείο ανέβηκε επιτυχώς.")

            tk.Button(self, text="Ανέβασμα Αρχείου", command=upload_note).pack(pady=5)

        # Display notes with download buttons
        notes_frame = tk.Frame(self)
        notes_frame.pack(fill="both", expand=True, padx=20)

        if not self.current_user.subscription:
            notes = [n for n in study_groups[self.group_selected]["notes"]
                     if n not in study_groups[self.group_selected]["subscriptions_required"]]
        else:
            notes = study_groups[self.group_selected]["notes"]

        for note in notes:
            note_frame = tk.Frame(notes_frame)
            note_frame.pack(fill="x", pady=2)
            tk.Label(note_frame, text=os.path.basename(note)).pack(side=tk.LEFT)
            
            def download_note(file_path=note):
                save_path = filedialog.asksaveasfilename(
                    defaultextension=os.path.splitext(file_path)[1],
                    initialfile=os.path.basename(file_path)
                )
                if save_path:
                    try:
                        # Here you would actually copy the file
                        messagebox.showinfo("Επιτυχία", "Το αρχείο κατέβηκε επιτυχώς.")
                    except:
                        messagebox.showerror("Σφάλμα", "Σφάλμα κατά το κατέβασμα του αρχείου.")

            tk.Button(note_frame, text="Λήψη", command=lambda f=note: download_note(f)).pack(side=tk.RIGHT)

        # Create button frame at the bottom
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Επιστροφή", 
                  command=self.create_group_home).pack(side=tk.LEFT, padx=5)

    def lessons_section(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header with only title
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", pady=10)
        tk.Label(header_frame, text="Μαθήματα", font=("Arial", 14)).pack(side=tk.LEFT, padx=20)

        # Initialize lessons list if it doesn't exist
        if "lessons" not in study_groups[self.group_selected]:
            study_groups[self.group_selected]["lessons"] = []

        # Show all lessons with their status
        lessons_frame = tk.Frame(self)
        lessons_frame.pack(fill="both", expand=True, padx=20)
        
        if not study_groups[self.group_selected]["lessons"]:
            tk.Label(lessons_frame, text="Δεν υπάρχουν προγραμματισμένα μαθήματα").pack(pady=5)

        for i, (time, status) in enumerate(study_groups[self.group_selected]["lessons"]):
            lesson_frame = tk.Frame(lessons_frame)
            lesson_frame.pack(fill="x", pady=2)
            status_text = "Διαθέσιμο" if status == "available" else "Κρατημένο"
            tk.Label(lesson_frame, text=f"{time} - {status_text}").pack(side=tk.LEFT)
            
            if not self.current_user.is_teacher and status == "available":
                def choose_time(t=i):
                    study_groups[self.group_selected]["lessons"][t] = (
                        study_groups[self.group_selected]["lessons"][t][0], 
                        "reserved"
                    )
                    # Notify teacher
                    for member in study_groups[self.group_selected]["members"]:
                        if member == "prof@gmail.com":  # Explicitly check for teacher's email
                            notification_msg = (f"Ο φοιτητής {self.current_user.email} "
                                             f"έκλεισε το μάθημα στις {time}")
                            self.send_notification(member, notification_msg)
                            self.save_data()  # Save changes immediately
                    
                    messagebox.showinfo("Επιτυχία", "Το μάθημα κρατήθηκε επιτυχώς!")
                    self.lessons_section()
                tk.Button(lesson_frame, text="Κράτηση", command=choose_time).pack(side=tk.RIGHT)

        if self.current_user.is_teacher:
            add_lesson_frame = tk.Frame(self)
            add_lesson_frame.pack(pady=10)
            
            # Calendar for date selection
            tk.Label(add_lesson_frame, text="Επιλέξτε ημερομηνία:").pack(pady=5)
            cal = Calendar(add_lesson_frame, selectmode='day', 
                         year=2025, month=5, day=27,
                         locale='el_GR')
            cal.pack(pady=5)
            
            # Time selection
            time_frame = tk.Frame(add_lesson_frame)
            time_frame.pack(pady=5)
            tk.Label(time_frame, text="Επιλέξτε ώρα:").pack(side=tk.LEFT)
            
            # Create list of hours (8:00 - 20:00)
            hours = [f"{h:02d}:00" for h in range(8, 21)]
            hour_var = tk.StringVar()
            hour_combo = ttk.Combobox(time_frame, 
                                    values=hours,
                                    textvariable=hour_var,
                                    width=10,
                                    state="readonly")
            hour_combo.set("08:00")  # default value
            hour_combo.pack(side=tk.LEFT, padx=5)

            def add_lesson():
                selected_date = cal.get_date()  # Returns date in format "MM/DD/YY"
                selected_time = hour_var.get()
                
                # Convert to proper datetime format
                try:
                    # Split the date into parts
                    month, day, year = selected_date.split('/')
                    # Convert 2-digit year to 4-digit year
                    year = '20' + year
                    # Create proper date string
                    date_str = f"{year}-{month:0>2}-{day:0>2}"
                    datetime_str = f"{date_str} {selected_time}"
                    
                    if "lessons" not in study_groups[self.group_selected]:
                        study_groups[self.group_selected]["lessons"] = []
                        
                    study_groups[self.group_selected]["lessons"].append((datetime_str, "available"))
                    self.save_data()  # Save immediately after adding lesson
                    
                    # Notify all students
                    for member in study_groups[self.group_selected]["members"]:
                        if member != self.current_user.email:
                            self.send_notification(
                                member,
                                f"Προστέθηκε νέο μάθημα στις {datetime_str}"
                            )
                    
                    messagebox.showinfo("Επιτυχία", "Το μάθημα προστέθηκε επιτυχώς!")
                    self.lessons_section()  # Refresh the lessons section
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την προσθήκη μαθήματος: {str(e)}")

            tk.Button(add_lesson_frame, text="Προσθήκη", 
                     command=add_lesson).pack(pady=10)

        # Create button frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Επιστροφή", 
                  command=self.create_group_home).pack(side=tk.LEFT, padx=5)

    def delete_group(self):
        confirm = messagebox.askyesno("Επιβεβαίωση", "Θέλετε σίγουρα να διαγράψετε την ομάδα;")
        if confirm:
            del study_groups[self.group_selected]
            user_groups.remove(self.group_selected)
            self.save_data()  # Save after deleting group
            messagebox.showinfo("Ολοκληρώθηκε", "Η ομάδα διαγράφηκε.")
            self.create_group_selection_screen()

    def view_members(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        tk.Label(self, text="Μέλη Ομάδας", font=("Arial", 14)).pack(pady=10)
        
        members_frame = tk.Frame(self)
        members_frame.pack(fill="both", expand=True, padx=20)
        
        for member in study_groups[self.group_selected]["members"]:
            member_frame = tk.Frame(members_frame)
            member_frame.pack(fill="x", pady=2)
            tk.Label(member_frame, text=member).pack(side=tk.LEFT)
            
            if self.current_user.is_teacher and member != self.current_user.email:
                def block_user(user=member):
                    if self.group_selected not in blocked_users:
                        blocked_users[self.group_selected] = []
                    blocked_users[self.group_selected].append(user)
                    messagebox.showinfo("Επιτυχία", f"Ο χρήστης {user} αποκλείστηκε.")
                    self.view_members()
                
                tk.Button(member_frame, text="Αποκλεισμός", 
                         command=block_user).pack(side=tk.RIGHT)
        
        # Create button frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Επιστροφή", 
                  command=self.create_group_home).pack(pady=5)

    def send_notification(self, user_email, message):
        notification = {
            "user": user_email,
            "message": message,
            "read": False,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.notifications.append(notification)
        self.save_notifications()

    def save_notifications(self):
        """Save notifications to file"""
        with open('notifications.json', 'w', encoding='utf-8') as f:
            json.dump(self.notifications, f, ensure_ascii=False, indent=4)

    def load_notifications(self):
        """Load notifications from file"""
        try:
            with open('notifications.json', 'r', encoding='utf-8') as f:
                self.notifications = json.load(f)
        except FileNotFoundError:
            self.notifications = []

if __name__ == "__main__":
    def login_gui():
        def try_login():
            email = email_entry.get()
            if email not in ["prof@gmail.com", "student@gmail.com"]:
                messagebox.showerror("Σφάλμα", "Δεν επιτρέπεται η πρόσβαση για αυτό το email.")
                return
            global current_user
            current_user = User(email)
            login.destroy()
            StudyGroupApp(current_user).mainloop()

        login = tk.Tk()
        login.title("Σύνδεση")
        login.geometry("300x200")

        tk.Label(login, text="Email:").pack(pady=10)
        email_entry = tk.Entry(login)
        email_entry.pack()

        tk.Button(login, text="Σύνδεση", command=try_login).pack(pady=20)
        login.mainloop()

    login_gui()
