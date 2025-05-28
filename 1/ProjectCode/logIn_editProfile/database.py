from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, event
from sqlalchemy.orm import declarative_base, sessionmaker
import hashlib
import logging
import re
import json

# Setup logging for database operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# DB setup
Base = declarative_base()
engine = create_engine("sqlite:///students.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String, unique=True)
    school = Column(String)
    subscription = Column(Boolean, default=False)
    profile_image_url = Column(String, default="")
    bio = Column(Text, default="")
    phone = Column(String, default="")
    password_hash = Column(String)

    def __repr__(self):
        return f"<Student {self.name} {self.surname}>"

    def to_dict(self):
        """Convert student object to dictionary for logging"""
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'school': self.school,
            'phone': self.phone,
            'bio': self.bio
        }

@event.listens_for(Student, 'after_insert')
def receive_after_insert(mapper, connection, target):
    student_data = target.to_dict()
    logger.info("\n=== Νέα Εγγραφή Χρήστη ===")
    logger.info(f"Όνομα: {student_data['name']}")
    logger.info(f"Επώνυμο: {student_data['surname']}")
    logger.info(f"Email: {student_data['email']}")
    logger.info(f"Σχολή: {student_data['school']}")
    logger.info("========================")

Base.metadata.create_all(engine)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Dummy data structure
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

def save_data():
    """Save data to JSON file"""
    data = {
        'study_groups': study_groups,
        'blocked_users': blocked_users,
        'user_groups': user_groups
    }
    with open('study_groups_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    """Load data from JSON file"""
    global study_groups, blocked_users, user_groups
    try:
        with open('study_groups_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            study_groups = data['study_groups']
            blocked_users = data['blocked_users']
            user_groups = data['user_groups']
    except FileNotFoundError:
        # If file doesn't exist, use default data
        save_data()