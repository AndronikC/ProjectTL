from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shmeioseis import Base, Note  # Αν το αρχείο σου έχει άλλο όνομα, άλλαξε αυτό
from datetime import datetime

engine = create_engine("sqlite:///study_platform.db")
Session = sessionmaker(bind=engine)
session = Session()

# Παράδειγμα σημειώσεων για υπάρχοντα course_id
sample_notes = [
    Note(uploader_id=2, course_id=1, title="Δομές Δεδομένων - Εισαγωγή", file_path="notes/dd_intro.pdf", is_locked=0, is_paid=0),
    Note(uploader_id=2, course_id=1, title="Δομές Δεδομένων - Προχωρημένα", file_path="notes/dd_advanced.pdf", is_locked=0, is_paid=1),
    Note(uploader_id=5, course_id=3, title="Μικροοικονομία - Βασικά", file_path="notes/micro_basics.pdf", is_locked=0, is_paid=0)
]

session.add_all(sample_notes)
session.commit()
print("✅ Σημειώσεις προστέθηκαν επιτυχώς.")
