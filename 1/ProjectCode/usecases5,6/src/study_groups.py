import json
from tkinter import ttk, messagebox, filedialog
import os

GROUPS_FILE = "groups.json"

def load_groups():
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Αν δεν υπάρχει αρχείο, ξεκίνα με default ομάδα
    return [
        {"id": 1, "name": "Ομάδα Μαθηματικών", "members": ["geo@gmail.com", "prof@gmail.com"], "notes": [], "lessons": [], "messages": [], "notifications": []},
    ]

def save_groups(groups):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

def show_study_groups_screen(app, user):
    app.clear()
    groups = load_groups()
    ttk.Label(app, text="Επέλεξε ομάδα μελέτης:", font=("Arial", 14)).pack(pady=10)
    user_groups = [g for g in groups if user.email in g["members"]]

    if not user_groups:
        ttk.Label(app, text="Δεν είσαι εγγεγραμμένος σε κάποια ομάδα.", foreground="red").pack(pady=10)
        ttk.Button(app, text="Πίσω", command=app.show_profile).pack(pady=10)
        return

    listbox = ttk.Treeview(app, columns=("name",), show="headings", height=6)
    listbox.heading("name", text="Όνομα Ομάδας")
    for group in user_groups:
        listbox.insert("", "end", values=(group["name"],))
    listbox.pack(pady=10)

    def select_group():
        selected = listbox.selection()
        if not selected:
            messagebox.showwarning("Προσοχή", "Επέλεξε μια ομάδα.")
            return
        idx = listbox.index(selected[0])
        group = user_groups[idx]
        show_group_main_screen(app, user, group, groups)

    ttk.Button(app, text="Επιλογή", command=select_group).pack(pady=5)
    ttk.Button(app, text="Πίσω", command=app.show_profile).pack(pady=5)

def show_group_main_screen(app, user, group, all_groups):
    app.clear()
    ttk.Label(app, text=f"Κεντρική σελίδα ομάδας: {group['name']}", font=("Arial", 14)).pack(pady=10)
    is_prof = user.email == "prof@gmail.com"

    if is_prof:
        ttk.Button(app, text="Ανέβασμα Σημειώσεων", command=lambda: upload_note(app, group, all_groups)).pack(pady=5)
        ttk.Button(app, text="Διαχείριση Ωρών Μαθήματος", command=lambda: manage_lessons(app, group, all_groups)).pack(pady=5)
        ttk.Button(app, text="Διαγραφή Ομάδας", command=lambda: delete_group(app, group, user, all_groups)).pack(pady=5)
        ttk.Button(app, text="Αποκλεισμός Μέλους", command=lambda: block_member(app, group, user, all_groups)).pack(pady=5)
    else:
        ttk.Button(app, text="Λήψη Σημειώσεων", command=lambda: download_notes(app, group, all_groups)).pack(pady=5)
        ttk.Button(app, text="Επιλογή Ώρας Μαθήματος", command=lambda: select_lesson(app, group, user, all_groups)).pack(pady=5)
    ttk.Button(app, text="Μηνύματα", command=lambda: show_messages(app, group, user, all_groups)).pack(pady=5)
    ttk.Button(app, text="Πίσω", command=lambda: show_study_groups_screen(app, user)).pack(pady=10)

    # Ειδοποιήσεις
    notifications = [n["text"] for n in group.get("notifications", []) if n.get("for") in (None, user.email)]
    if notifications:
        ttk.Label(app, text="Ειδοποιήσεις:", font=("Arial", 10, "bold")).pack(pady=(20, 0))
        for note in notifications[-5:]:  # Εμφάνιση των 5 πιο πρόσφατων
            ttk.Label(app, text=note, foreground="blue").pack()

def upload_note(app, group, all_groups):
    file_path = filedialog.askopenfilename(filetypes=[("PDF αρχεία", "*.pdf"), ("Όλα τα αρχεία", "*.*")])
    if file_path:
        group["notes"].append({
            "filename": os.path.basename(file_path),
            "filepath": file_path
        })
        # Ειδοποίηση σε όλους εκτός του καθηγητή
        for member in group["members"]:
            if member != "prof@gmail.com":
                add_notification(group, f"Ο καθηγητής ανέβασε νέα σημείωση: {os.path.basename(file_path)}", for_user=member)
        save_groups(all_groups)
        messagebox.showinfo("Επιτυχία", "Το αρχείο ανέβηκε (demo λειτουργία).")

def download_notes(app, group, all_groups):
    app.clear()
    ttk.Label(app, text="Διαθέσιμες σημειώσεις:", font=("Arial", 12)).pack(pady=10)
    if not group["notes"]:
        ttk.Label(app, text="Δεν υπάρχουν σημειώσεις.").pack(pady=10)
    else:
        for note in group["notes"]:
            # Υποστήριξη και για παλιά (string) και για νέα (dict) μορφή
            if isinstance(note, dict):
                filename = note.get("filename", "Σημείωση")
                filepath = note.get("filepath", "")
            else:
                filename = note
                filepath = ""
            def make_download_func(filename=filename, filepath=filepath):
                def download():
                    if not filepath:
                        messagebox.showerror("Σφάλμα", "Το αρχείο δεν είναι διαθέσιμο για λήψη (παλιά σημείωση).")
                        return
                    dest = filedialog.asksaveasfilename(initialfile=filename)
                    if dest:
                        try:
                            with open(filepath, "rb") as src, open(dest, "wb") as dst:
                                dst.write(src.read())
                            messagebox.showinfo("Επιτυχία", f"Το αρχείο αποθηκεύτηκε ως {dest}")
                        except Exception as e:
                            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη λήψη: {e}")
                return download
            ttk.Button(app, text=filename, command=make_download_func()).pack(pady=2)
    ttk.Button(app, text="Πίσω", command=lambda: show_group_main_screen(app, app.user, group, all_groups)).pack(pady=10)

def manage_lessons(app, group, all_groups):
    app.clear()
    ttk.Label(app, text="Διαχείριση Ωρών Μαθήματος", font=("Arial", 12)).pack(pady=10)
    entry = ttk.Entry(app)
    entry.pack()
    ttk.Label(app, text="Π.χ. 2024-06-01 18:00").pack()
    def add_time():
        time = entry.get()
        if time:
            group["lessons"].append(time)
            # Ειδοποίηση σε όλους εκτός του καθηγητή
            for member in group["members"]:
                if member != "prof@gmail.com":
                    add_notification(group, f"Ο καθηγητής ανέβασε νέα ώρα μαθήματος: {time}", for_user=member)
            save_groups(all_groups)
            messagebox.showinfo("Επιτυχία", "Η ώρα προστέθηκε.")
    ttk.Button(app, text="Προσθήκη ώρας", command=add_time).pack(pady=5)
    ttk.Button(app, text="Πίσω", command=lambda: show_group_main_screen(app, app.user, group, all_groups)).pack(pady=10)

def select_lesson(app, group, user, all_groups):
    app.clear()
    ttk.Label(app, text="Διαθέσιμες ώρες για μάθημα:", font=("Arial", 12)).pack(pady=10)
    if not group["lessons"]:
        ttk.Label(app, text="Δεν υπάρχουν διαθέσιμες ώρες.").pack(pady=10)
    else:
        for lesson in group["lessons"]:
            ttk.Button(app, text=lesson, command=lambda l=lesson: choose_lesson(app, group, user, l, all_groups)).pack(pady=2)
    ttk.Button(app, text="Πίσω", command=lambda: show_group_main_screen(app, user, group, all_groups)).pack(pady=10)

def choose_lesson(app, group, user, lesson, all_groups):
    # Αφαίρεση της ώρας από τη λίστα
    if lesson in group["lessons"]:
        group["lessons"].remove(lesson)
    add_notification(group, f"Ο/Η {user.email} κράτησε το μάθημα: {lesson}", for_user="prof@gmail.com")
    save_groups(all_groups)
    messagebox.showinfo("Επιτυχία", f"Έγινε κράτηση για το μάθημα: {lesson}")
    show_group_main_screen(app, user, group, all_groups)

def show_messages(app, group, user, all_groups):
    app.clear()
    ttk.Label(app, text="Μηνύματα", font=("Arial", 12)).pack(pady=10)
    messages = group.get("messages", [])
    for msg in messages:
        ttk.Label(app, text=f"{msg['from']}: {msg['text']}").pack(anchor="w")
    entry = ttk.Entry(app, width=40)
    entry.pack(pady=5)
    def send():
        text = entry.get()
        if text:
            messages.append({"from": user.email, "text": text})
            # Ειδοποίηση στον άλλο χρήστη
            other = "prof@gmail.com" if user.email != "prof@gmail.com" else next(m for m in group["members"] if m != "prof@gmail.com")
            add_notification(group, f"Νέο μήνυμα από {user.email}", for_user=other)
            save_groups(all_groups)
            show_messages(app, group, user, all_groups)
    ttk.Button(app, text="Αποστολή", command=send).pack(pady=5)
    ttk.Button(app, text="Πίσω", command=lambda: show_group_main_screen(app, user, group, all_groups)).pack(pady=10)

def delete_group(app, group, user, all_groups):
    if messagebox.askyesno("Διαγραφή", "Είσαι σίγουρος για τη διαγραφή της ομάδας;"):
        all_groups.remove(group)
        save_groups(all_groups)
        messagebox.showinfo("Διαγραφή", "Η ομάδα διαγράφηκε.")
        show_study_groups_screen(app, user)

def block_member(app, group, user, all_groups):
    app.clear()
    ttk.Label(app, text="Επιλογή μέλους για αποκλεισμό:", font=("Arial", 12)).pack(pady=10)
    for member in group["members"]:
        if member != "prof@gmail.com":
            ttk.Button(app, text=member, command=lambda m=member: confirm_block(app, group, user, m, all_groups)).pack(pady=2)
    ttk.Button(app, text="Πίσω", command=lambda: show_group_main_screen(app, user, group, all_groups)).pack(pady=10)

def confirm_block(app, group, user, member, all_groups):
    if messagebox.askyesno("Αποκλεισμός", f"Να αποκλειστεί ο χρήστης {member};"):
        group["members"].remove(member)
        save_groups(all_groups)
        messagebox.showinfo("Αποκλεισμός", f"Ο χρήστης {member} αποκλείστηκε.")
        show_group_main_screen(app, user, group, all_groups)

def add_notification(group, text, for_user=None):
    if "notifications" not in group:
        group["notifications"] = []
    group["notifications"].append({
        "text": text,
        "for": for_user  # None για όλους, ή email για συγκεκριμένο χρήστη
    })