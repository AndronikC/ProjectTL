import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# === Database Setup ===
Base = declarative_base()
engine = create_engine("sqlite:///study_platform.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# === Models ===
class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String)
    evaluations_given = relationship("Review", foreign_keys="Review.evaluator_id", back_populates="evaluator")
    evaluations_received = relationship("Review", foreign_keys="Review.evaluated_id", back_populates="evaluated")

class Review(Base):
    __tablename__ = "Evaluations"
    id = Column(Integer, primary_key=True)
    evaluator_id = Column(Integer, ForeignKey('Users.id'))
    evaluated_id = Column(Integer, ForeignKey('Users.id'))
    stars = Column(Integer)
    comment = Column(Text)
    date = Column(String)
    q1 = Column(Text)
    q2 = Column(Text)
    q3 = Column(Text)

    evaluator = relationship("User", foreign_keys=[evaluator_id], back_populates="evaluations_given")
    evaluated = relationship("User", foreign_keys=[evaluated_id], back_populates="evaluations_received")

# === GUI App ===
class EvaluationApp:
    def __init__(self, root, student):
        self.root = root
        self.student = student
        self.root.title("Αξιολόγηση Φοιτητή-Καθηγητή")

        tk.Label(root, text="Επιλέξτε Φοιτητή-Καθηγητή:", font=("Arial", 12)).pack(pady=5)
        self.profs = session.query(User).filter(User.role == 'tutor').all()

        self.prof_var = tk.StringVar(root)
        self.prof_var.set(self.profs[0].first_name)
        tk.OptionMenu(root, self.prof_var, *[p.first_name for p in self.profs]).pack()

        self.entries = []
        questions = [
            "1. Πώς θα σχολιάζατε την εμπειρία σας;",
            "2. Θα τον προτείνατε σε άλλους φοιτητές;",
            "3. Ποια στοιχεία του ξεχωρίσατε;"
        ]
        for q in questions:
            tk.Label(root, text=q, font=("Arial", 10)).pack()
            entry = tk.Entry(root, width=60)
            entry.pack()
            self.entries.append(entry)

        tk.Label(root, text="Βαθμολογία (0-5):", font=("Arial", 10)).pack(pady=5)
        self.rating_entry = tk.Entry(root)
        self.rating_entry.pack()

        tk.Label(root, text="Σχόλια:", font=("Arial", 10)).pack()
        self.comment_entry = tk.Entry(root, width=60)
        self.comment_entry.pack()

        tk.Button(root, text="Υποβολή Αξιολόγησης", command=self.submit_review, bg="lightgreen").pack(pady=10)
        tk.Button(root, text="Προβολή Όλων των Αξιολογήσεων", command=self.show_all_reviews, bg="lightblue").pack(pady=5)

    def submit_review(self):
        prof = session.query(User).filter_by(first_name=self.prof_var.get(), role='tutor').first()
        answers = [e.get().strip() for e in self.entries]
        if not all(answers):
            messagebox.showerror("Σφάλμα", "Οι απαντήσεις είναι υποχρεωτικές.")
            return

        try:
            rating = int(self.rating_entry.get())
            if rating < 0 or rating > 5:
                raise ValueError
        except ValueError:
            messagebox.showerror("Σφάλμα", "Η βαθμολογία πρέπει να είναι από 0 έως 5.")
            return

        comment = self.comment_entry.get()

        new_review = Review(
            evaluator=self.student,
            evaluated=prof,
            q1=answers[0],
            q2=answers[1],
            q3=answers[2],
            stars=rating,
            comment=comment,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        session.add(new_review)
        session.commit()
        messagebox.showinfo("Επιτυχία", "Η αξιολόγηση καταχωρήθηκε!")

    def show_all_reviews(self):
        window = tk.Toplevel(self.root)
        window.title("Όλες οι Αξιολογήσεις")

        tutors = session.query(User).filter(User.role == 'tutor').all()
        for tutor in tutors:
            reviews = tutor.evaluations_received
            avg = round(sum(r.stars for r in reviews)/len(reviews), 2) if reviews else "-"
            tk.Label(window, text=f"{tutor.first_name} {tutor.last_name} - ⭐ Μέσος Όρος: {avg}", font=("Arial", 11, "bold"), fg="blue").pack(anchor="w", padx=10)
            for r in reviews:
                evaluator = r.evaluator
                frame = tk.Frame(window, bd=1, relief="solid", padx=5, pady=2)
                frame.pack(fill="x", padx=10, pady=3)
                tk.Label(frame, text=f"{evaluator.first_name} ➤ {r.stars} ⭐: {r.comment}", anchor="w", justify="left").pack(anchor="w")
                btn = tk.Button(frame, text="🗑 Διαγραφή", command=lambda rid=r.id: self.delete_review(rid))
                btn.pack(anchor="e")

    def delete_review(self, review_id):
        if messagebox.askyesno("Επιβεβαίωση", "Είστε σίγουροι για τη διαγραφή;"):
            review = session.get(Review, review_id)
            session.delete(review)
            session.commit()
            messagebox.showinfo("Ολοκληρώθηκε", "Η αξιολόγηση διαγράφηκε.")
            self.show_all_reviews()

# === Εκκίνηση Εφαρμογής ===
if __name__ == "__main__":
    student = session.query(User).filter_by(id=1, role='student').first()
    if not student:
        student = User(first_name="Γιώργος", last_name="Παπαδόπουλος", role="student")
        session.add(student)
        session.commit()
    root = tk.Tk()
    app = EvaluationApp(root, student)
    root.mainloop()
