# Αντικειμενοστραφής έκδοση της λειτουργίας "Αναζήτηση Ομάδας Μελέτης"
import tkinter as tk
from tkinter import ttk, messagebox, Listbox
import sqlite3

# --- Globals ---
CURRENT_USER_ID = None
CURRENT_USERNAME = None

# --- Κλάσεις ---
class DatabaseManager:
    def __init__(self, db_name="study_platform.db"):
        self.db_name = db_name

    def execute(self, query, params=(), fetchone=False, fetchall=False):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute(query, params)
        result = None
        if fetchone:
            result = cur.fetchone()
        elif fetchall:
            result = cur.fetchall()
        conn.commit()
        conn.close()
        return result

    def get_autofill_values(self, column_name, table):
        query = f"SELECT DISTINCT {column_name} FROM {table}"
        return [row[0] for row in self.execute(query, fetchall=True)]


class HomePage:
    def __init__(self, root, ui_manager):
        self.root = root
        self.ui = ui_manager

    def navigateToStudyGroups(self):
        self.ui.displayFilters()


class SearchGroupsPage:
    def __init__(self, ui_manager):
        self.ui = ui_manager

    def sendFilters(self, criteria):
        self.ui.getGroups(criteria)


class ResultsPage:
    def __init__(self, ui_manager):
        self.ui = ui_manager

    def chooseGroup(self):
        self.ui.submitJoinRequest()


class UIManager:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill="both", expand=True)

        self.user_label = ttk.Label(self.frame, text="Χρήστης: Δεν είστε συνδεδεμένος", foreground="gray")
        self.user_label.grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(self.frame, text="Σχολή:").grid(row=1, column=0, sticky="w")
        self.department_entry = ttk.Entry(self.frame, width=40)
        self.department_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.frame, text="Μάθημα:").grid(row=2, column=0, sticky="w")
        self.course_entry = ttk.Entry(self.frame, width=40)
        self.course_entry.grid(row=2, column=1, pady=5)

        ttk.Label(self.frame, text="Τρόπος Μελέτης:").grid(row=3, column=0, sticky="w")
        self.mode_var = tk.StringVar()
        self.mode_combo = ttk.Combobox(self.frame, textvariable=self.mode_var, state="readonly", width=38)
        self.mode_combo["values"] = ["", "εξ αποστάσεως", "δια ζώσης", "υβριδικό"]
        self.mode_combo.grid(row=3, column=1, pady=5)

        ttk.Button(self.frame, text="Εμφάνιση Όλων", command=lambda: self.getGroups(False)).grid(row=4, column=0, pady=10)
        ttk.Button(self.frame, text="Εφαρμογή Φίλτρων", command=lambda: self.getGroups(True)).grid(row=4, column=1, pady=10)

        columns = ("Τίτλος", "Διδάσκων", "Τρόπος Μελέτης")
        self.result_list = ttk.Treeview(self.frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.result_list.heading(col, text=col)
            self.result_list.column(col, anchor="center", width=200)
        self.result_list.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(self.frame, text="Υποβολή Αίτησης", command=self.submitJoinRequest).grid(row=6, column=0, columnspan=2, pady=10)

        self.attach_autofill(self.department_entry, self.db.get_autofill_values("name", "Departments"))
        self.attach_autofill(self.course_entry, self.db.get_autofill_values("title", "Courses"))

    def displayFilters(self):
        self.root.deiconify()

    def getGroups(self, criteria_applied):
        # Λήψη φίλτρων από τον χρήστη
        department, course, study_mode = self.getGroupsCriteria()

        # Επεξεργασία φίλτρων για να μην είναι κενά
        department_filter = f"%{department}%" if department else "%"
        course_filter = f"%{course}%" if course else "%"
        study_mode_filter = f"%{study_mode}%" if study_mode else "%"

        # Δημιουργία ερωτήματος SQL
        query = '''
        SELECT c.title || ' - ' || d.name, u.last_name, sg.study_mode
        FROM StudyGroups sg
        JOIN Courses c ON sg.course_id = c.id
        JOIN Departments d ON c.department_id = d.id
        JOIN Users u ON sg.creator_id = u.id
        WHERE d.name LIKE ? AND c.title LIKE ? AND sg.study_mode LIKE ? AND sg.is_active = 1
        '''
        rows = self.db.execute(query, (department_filter, course_filter, study_mode_filter), fetchall=True)

        # Εμφάνιση αποτελεσμάτων
        self.displayGroupList(rows)

    def displayGroupList(self, rows):
        # Καθαρισμός προηγούμενων αποτελεσμάτων
        self.result_list.delete(*self.result_list.get_children())

        if not rows:
            # Αν δεν υπάρχουν αποτελέσματα, εμφάνιση μηνύματος
            self.returnNoGroupsFound([])
            return

        # Εισαγωγή αποτελεσμάτων στη λίστα
        for row in rows:
            self.result_list.insert("", "end", values=row)

        # Εμφάνιση εργαλείων για τις ομάδες
        self.showGroups()

    def returnAvailableGroups(self, groupsList):
        return groupsList

    def showGroups(self):
        self.displayTools()

    def displayTools(self):
        pass

    def chooseGroup(self):
        self.submitJoinRequest()

    def enableGroupAccess(self):
        pass

    def checkEligibility(self, user_id):
        return True

    def getGroupsCriteria(self):
        return self.department_entry.get(), self.course_entry.get(), self.mode_var.get()

    def submitJoinRequest(self):
        self.request_to_join_group()

    def rejectRequest(self):
        messagebox.showwarning("Απόρριψη", "Η αίτησή σας απορρίφθηκε.")

    def displayError(self, message):
        messagebox.showerror("Σφάλμα", message)

    def returnNoGroupsFound(self, emptyResult):
        messagebox.showinfo("Αποτέλεσμα", "Δεν βρέθηκαν ομάδες που να πληρούν τα κριτήριά σας.")

    def modifyFilters(self):
        messagebox.showinfo("Τροποποίηση", "Μπορείτε να αλλάξετε τα φίλτρα αναζήτησης και να ξαναδοκιμάσετε.")

    def request_to_join_group(self):
        global CURRENT_USER_ID
        if CURRENT_USER_ID is None:
            self.show_login_window()
            return

        selected = self.result_list.focus()
        if not selected:
            messagebox.showwarning("Προσοχή", "Επιλέξτε ομάδα για αίτηση.")
            return

        values = self.result_list.item(selected, 'values')
        full_title, tutor_last_name, _ = values
        course_title = full_title.split(" - ")[0]

        query = '''SELECT sg.id, sg.creator_id, sg.current_members, sg.max_members FROM StudyGroups sg
                   JOIN Courses c ON sg.course_id = c.id
                   JOIN Users u ON sg.creator_id = u.id
                   WHERE c.title=? AND u.last_name=?'''
        result = self.db.execute(query, (course_title, tutor_last_name), fetchone=True)
        if not result:
            self.displayError("Η ομάδα δεν βρέθηκε.")
            return

        group_id, creator_id, current_members, max_members = result

        if creator_id == CURRENT_USER_ID:
            messagebox.showwarning("Μη διαθέσιμη ενέργεια", "Είστε ήδη δημιουργός αυτής της ομάδας.")
            return

        if current_members >= max_members:
            messagebox.showwarning("Η ομάδα είναι πλήρης", "Η ομάδα μελέτης που επιλέξατε έχει ήδη συμπληρωθεί.")
            return

        query = "SELECT id FROM StudyGroupRequests WHERE user_id=? AND group_id=? AND status='pending'"
        if self.db.execute(query, (CURRENT_USER_ID, group_id), fetchone=True):
            messagebox.showinfo("Ήδη Υποβλήθηκε", "Έχετε ήδη υποβάλει αίτηση για αυτή την ομάδα.")
            return

        insert_query = "INSERT INTO StudyGroupRequests (user_id, group_id, status) VALUES (?, ?, ?)"
        self.db.execute(insert_query, (CURRENT_USER_ID, group_id, "pending"))
        messagebox.showinfo("Επιτυχία", "Η αίτηση στάλθηκε επιτυχώς!")

    def attach_autofill(self, entry_widget, values_list):
        listbox = Listbox(entry_widget.master, height=4)
        listbox.place_forget()

        def update_listbox(event=None):
            typed = entry_widget.get().lower()
            matches = [v for v in values_list if typed in v.lower()]
            listbox.delete(0, 'end')
            for val in matches:
                listbox.insert('end', val)
            if matches:
                listbox.place(x=entry_widget.winfo_x(), y=entry_widget.winfo_y() + entry_widget.winfo_height())
            else:
                listbox.place_forget()

        def fill_entry(event):
            if listbox.curselection():
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, listbox.get(listbox.curselection()))
            listbox.place_forget()

        def hide_listbox_on_click(event):
            if event.widget != listbox and event.widget != entry_widget:
                listbox.place_forget()

        entry_widget.bind('<KeyRelease>', update_listbox)
        listbox.bind("<<ListboxSelect>>", fill_entry)
        entry_widget.master.bind("<Button-1>", hide_listbox_on_click, add="+")

    def show_login_window(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Σύνδεση")
        tk.Label(login_window, text="Email:").pack(pady=5)
        username_entry = tk.Entry(login_window)
        username_entry.pack()
        tk.Label(login_window, text="Κωδικός:").pack(pady=5)
        password_entry = tk.Entry(login_window, show="*")
        password_entry.pack()
        tk.Button(login_window, text="Σύνδεση", command=lambda: self.login_user(username_entry.get(), password_entry.get(), login_window)).pack(pady=10)

    def login_user(self, email, password, window):
        global CURRENT_USER_ID, CURRENT_USERNAME
        query = "SELECT id, first_name FROM Users WHERE email=? AND password=?"
        result = self.db.execute(query, (email, password), fetchone=True)
        if result:
            CURRENT_USER_ID, CURRENT_USERNAME = result
            messagebox.showinfo("Επιτυχία", f"Συνδεθήκατε ως {CURRENT_USERNAME}!")
            self.user_label.config(text=f"Χρήστης: {CURRENT_USERNAME}")
            window.destroy()
        else:
            self.displayError("Λάθος email ή κωδικός.")

# --- Εκκίνηση Εφαρμογής ---
root = tk.Tk()
root.title("Αναζήτηση Ομάδας Μελέτης")
root.geometry("700x600")
root.resizable(False, False)

ui_manager = UIManager(root)
home_page = HomePage(root, ui_manager)
search_page = SearchGroupsPage(ui_manager)
results_page = ResultsPage(ui_manager)

home_page.navigateToStudyGroups()
root.mainloop()
