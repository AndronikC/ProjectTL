import sqlite3
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

# Σύνδεση με βάση
conn = sqlite3.connect("study_platform.db")
cur = conn.cursor()

# Δημιουργία Πινάκων
cur.execute("""
CREATE TABLE IF NOT EXISTS Departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES Departments(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT CHECK(role IN ('student', 'tutor')),
    department_id INTEGER,
    is_verified INTEGER DEFAULT 0,
    academic_id TEXT,
    verification_code TEXT,
    phone TEXT,
    bio TEXT,
    profile_image TEXT,
    FOREIGN KEY (department_id) REFERENCES Departments(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS StudyGroups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    course_id INTEGER,
    creator_id INTEGER,
    max_members INTEGER,
    current_members INTEGER,
    date TEXT,
    time TEXT,
    study_mode TEXT,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (course_id) REFERENCES Courses(id),
    FOREIGN KEY (creator_id) REFERENCES Users(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS StudyGroupRequests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    group_id INTEGER,
    status TEXT CHECK(status IN ('pending', 'accepted', 'rejected', 'cancelled')) DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (group_id) REFERENCES StudyGroups(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    is_active INTEGER DEFAULT 1,
    start_date TEXT,
    end_date TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    status TEXT CHECK(status IN ('success', 'failed')),
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uploader_id INTEGER,
    course_id INTEGER,
    title TEXT,
    file_path TEXT,
    is_locked INTEGER DEFAULT 0,
    is_paid INTEGER DEFAULT 0,
    FOREIGN KEY (uploader_id) REFERENCES Users(id),
    FOREIGN KEY (course_id) REFERENCES Courses(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluator_id INTEGER,
    evaluated_id INTEGER,
    stars INTEGER CHECK(stars BETWEEN 0 AND 5),
    comment TEXT,
    date TEXT,
    FOREIGN KEY (evaluator_id) REFERENCES Users(id),
    FOREIGN KEY (evaluated_id) REFERENCES Users(id)
)
""")

cur.execute("ALTER TABLE Evaluations ADD COLUMN q1 TEXT")
cur.execute("ALTER TABLE Evaluations ADD COLUMN q2 TEXT")
cur.execute("ALTER TABLE Evaluations ADD COLUMN q3 TEXT")

cur.execute("""
CREATE TABLE IF NOT EXISTS Messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    receiver_id INTEGER,
    content TEXT,
    timestamp TEXT,
    FOREIGN KEY (sender_id) REFERENCES Users(id),
    FOREIGN KEY (receiver_id) REFERENCES Users(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    date TEXT,
    seen INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(id)
)
""")

# 2. Εισαγωγή Τμημάτων (Departments)
departments = [
    ("Πληροφορικής",), ("Ηλεκτρολόγων Μηχανικών",), ("Ιατρικής",),
    ("Νομικής",), ("Οικονομικών Επιστημών",), ("Φυσικής",), ("Μαθηματικών",)
]
cur.executemany("INSERT INTO Departments (name) VALUES (?)", departments)

# 3. Εισαγωγή Μαθημάτων (Courses)
courses = [
    ("Δομές Δεδομένων", 1), ("Λειτουργικά Συστήματα", 1), ("Μικροοικονομία", 5),
    ("Εισαγωγή στο Δίκαιο", 4), ("Ανατομία", 3), ("Ηλεκτρομαγνητισμός", 6),
    ("Απειροστικός Λογισμός", 7), ("Προγραμματισμός", 1), ("Ενισχυτική Μάθηση", 1),
    ("Ηλεκτρικά Κυκλώματα", 2), ("Ιστορία Δικαίου", 4), ("Στατιστική", 5),
    ("Κλασική Μηχανική", 6), ("Γραμμική Άλγεβρα", 7), ("Διοίκηση Επιχειρήσεων", 5)
]
cur.executemany("INSERT INTO Courses (title, department_id) VALUES (?, ?)", courses)

# 4. Εισαγωγή Χρηστών (Users)
users = [
    ("Γιάννης", "Παπαδόπουλος", "giannis1@example.com", "pass123", "student", 1),
    ("Μαρία", "Κωνσταντίνου", "maria2@example.com", "pass123", "tutor", 2),
    ("Αλέξης", "Νικολάου", "alexis3@example.com", "pass123", "student", 1),
    ("Ελένη", "Αναστασίου", "eleni4@example.com", "pass123", "student", 3),
    ("Πέτρος", "Γεωργίου", "petros5@example.com", "pass123", "tutor", 5),
    ("Κατερίνα", "Μιχαήλ", "katerina6@example.com", "pass123", "student", 4),
    ("Νίκος", "Σταματίου", "nikos7@example.com", "pass123", "student", 6),
    ("Χρήστος", "Λεωνίδας", "xristos8@example.com", "pass123", "student", 7),
    ("Άννα", "Βασιλείου", "anna9@example.com", "pass123", "student", 1),
    ("Σπύρος", "Διαμαντής", "spyros10@example.com", "pass123", "tutor", 2)
]
cur.executemany("""
INSERT INTO Users (first_name, last_name, email, password, role, department_id)
VALUES (?, ?, ?, ?, ?, ?)
""", users)

# 5. Εισαγωγή Ομάδων Μελέτης (StudyGroups)
groups = [
    ("Δομές Δεδομένων - Παπαδόπουλος", 1, 1, 5, 2, "2025-06-10", "16:00", "Δια ζώσης"),
    ("Λειτουργικά Συστήματα - Νικολάου", 2, 3, 6, 6, "2025-06-12", "14:00", "Εξ αποστάσεως"),
    ("Ανατομία - Αναστασίου", 5, 4, 8, 4, "2025-06-15", "11:00", "Υβριδικό"),
    ("Μικροοικονομία - Γεωργίου", 3, 5, 5, 5, "2025-06-20", "18:00", "Δια ζώσης"),
    ("Ηλεκτρικά Κυκλώματα - Κωνσταντίνου", 10, 2, 7, 2, "2025-06-18", "13:00", "Εξ αποστάσεως"),
    ("Απειροστικός Λογισμός - Λεωνίδας", 7, 8, 4, 1, "2025-06-22", "09:00", "Υβριδικό"),
    ("Προγραμματισμός - Παπαδόπουλος", 8, 1, 6, 3, "2025-06-25", "10:00", "Δια ζώσης"),
    ("Ιστορία Δικαίου - Μιχαήλ", 11, 6, 5, 1, "2025-06-28", "17:00", "Υβριδικό"),
    ("Γραμμική Άλγεβρα - Βασιλείου", 14, 9, 4, 4, "2025-07-01", "15:00", "Εξ αποστάσεως"),
    ("Διοίκηση Επιχειρήσεων - Διαμαντής", 15, 10, 7, 3, "2025-07-03", "16:00", "Δια ζώσης")
]
cur.executemany("""
INSERT INTO StudyGroups (title, course_id, creator_id, max_members, current_members, date, time, study_mode)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", groups)

from datetime import datetime, timedelta

# --- Εισαγωγή Συνδρομών (Subscriptions) ---

# Παράδειγμα: δύο χρήστες αποκτούν συνδρομή (ο ένας ως student και ο άλλος ως tutor)
today = datetime.now().strftime("%Y-%m-%d")
end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

subscriptions = [
    (1, "student", 1, today, end_date),
    (2, "tutor", 1, today, end_date)
]

cur.executemany("""
INSERT INTO Subscriptions (user_id, type, is_active, start_date, end_date)
VALUES (?, ?, ?, ?, ?)
""", subscriptions)


# --- Εισαγωγή Πληρωμών (Payments) ---

payments = [
    (1, 6.99, "success", today),
    (2, 6.99, "success", today)
]

cur.executemany("""
INSERT INTO Payments (user_id, amount, status, date)
VALUES (?, ?, ?, ?)
""", payments)


# 6. Εισαγωγή αξιολογήσεων (evaluator_id, evaluated_id, stars, comment, date)
evaluations = [
    (1, 2, 4, 'Συνεργάσιμος και κατανοητός διδάσκων.', today),
    (3, 5, 5, 'Εξαιρετική εμπειρία μάθησης.', today),
    (4, 2, 3, 'Χρήσιμος, αλλά χρειάζεται βελτίωση στη δομή.', today),
    (6, 10, 4, 'Πολύ βοηθητικός και σαφής.', today),
    (7, 5, 2, 'Δεν εξήγησε αρκετά παραδείγματα.', today),
    (8, 2, 5, 'Έδωσε επιπλέον υλικό και βοήθησε πολύ.', today),
    (9, 10, 3, 'Καλή παρουσίαση, αλλά βιαστικός.', today),
    (1, 5, 4, 'Καλή προσέγγιση και οργάνωση ύλης.', today),
    (3, 10, 5, 'Πολύ επαγγελματική προσέγγιση.', today),
    (6, 2, 4, 'Σαφής και παραστατικός στις εξηγήσεις.', today)
]

# Εκτέλεση των inserts
cur.executemany("""
INSERT INTO Evaluations (evaluator_id, evaluated_id, stars, comment, date)
VALUES (?, ?, ?, ?, ?)
""", evaluations)

# 7. Notifications
notifications = [
    (1, "Νέα ομάδα μελέτης δημιουργήθηκε για το μάθημα Δομές Δεδομένων.", today, 0),
    (2, "Η αίτησή σας για την ομάδα μελέτης Λειτουργικά Συστήματα έγινε αποδεκτή.", today, 0),
    (3, "Υπενθύμιση: Η ομάδα μελέτης Ανατομία ξεκινά σε 1 ώρα.", today, 0),
    (4, "Η πληρωμή σας για τη συνδρομή ολοκληρώθηκε επιτυχώς.", today, 0),
    (5, "Νέα αξιολόγηση για τον διδάσκοντα Πέτρος Γεωργίου.", today, 0)
]

cur.executemany("""
INSERT INTO Notifications (user_id, content, date, seen)
VALUES (?, ?, ?, ?)
""", notifications)


# Αποθήκευση και Κλείσιμο
conn.commit()
conn.close()