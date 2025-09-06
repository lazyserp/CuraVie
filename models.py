# models.py (Revised and Cleaned)
import enum
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db
from flask_login import UserMixin

# --- Enums  ---
class GenderEnum(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class UserRoleEnum(enum.Enum):
    ADMIN = "admin"
    HEALTH_OFFICIAL = "health_official"
    NORMAL_USER = "normal_user"

class OccupationEnum(enum.Enum):
    CONSTRUCTION = "Construction"
    AGRICULTURE = "Agriculture"
    DOMESTIC_WORK = "Domestic Work"
    FACTORY = "Factory"
    FISHING = "Fishing"
    OTHER = "Other"

class DietTypeEnum(enum.Enum):
    VEG = "Vegetarian"
    NON_VEG = "Non-Vegetarian"
    EGGETARIAN = "Eggetarian"
    VEGAN = "Vegan"

class FrequencyEnum(enum.Enum):
    NEVER = "Never"
    OCCASIONALLY = "Occasionally"
    WEEKLY = "Weekly"
    DAILY = "Daily"

# --- Core Models ---

class User(db.Model,UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(Enum(UserRoleEnum), default=UserRoleEnum.NORMAL_USER, nullable=False)
    worker = db.relationship("Worker", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Worker(db.Model):
    __tablename__ = "workers"
    id = db.Column(db.Integer, primary_key=True)
    # A worker profile must be linked to a user account.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    
    # Basic Bio
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(Enum(GenderEnum), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    preferred_language = db.Column(db.String(50), default='en')

    # Occupational & Lifestyle Data
    occupation = db.Column(Enum(OccupationEnum), nullable=False)
    work_hours_per_day = db.Column(db.Integer)
    home_state = db.Column(db.String(100))
    smoking_habit = db.Column(Enum(FrequencyEnum), default=FrequencyEnum.NEVER)
    alcohol_consumption = db.Column(Enum(FrequencyEnum), default=FrequencyEnum.NEVER)
    diet_type = db.Column(Enum(DietTypeEnum))

    # Relationships
    user = db.relationship("User", back_populates="worker")
    health_records = db.relationship("HealthRecord", back_populates="worker", cascade="all, delete-orphan")
    medical_visits = db.relationship("MedicalVisit", back_populates="worker", cascade="all, delete-orphan")
    vaccinations = db.relationship("Vaccination", back_populates="worker", cascade="all, delete-orphan")

class HealthRecord(db.Model):
    __tablename__ = "health_records"
    id = db.Column(db.Integer, primary_key=True)
    # A health record must belong to a worker.
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"), nullable=False)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    any_chronic_disease = db.Column(db.String(255))

    worker = db.relationship("Worker", back_populates="health_records")


class HealthcareFacility(db.Model):
    __tablename__ = "healthcare_facilities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100)) # e.g., 'Clinic', 'Hospital', 'PHC'
    facility_license_number = db.Column(db.String(100), unique=True)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))


    medical_visits = db.relationship("MedicalVisit", back_populates="facility")

class MedicalVisit(db.Model):
    __tablename__ = "medical_visits"
    id = db.Column(db.Integer, primary_key=True)
    # foreign keys non-nullable for data integrity.
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"), nullable=False)
    facility_id = db.Column(db.Integer, db.ForeignKey("healthcare_facilities.id"), nullable=False)
    
    #doctor_name is  specific to a visit.
    doctor_name = db.Column(db.String(255))
    visit_date = db.Column(db.Date, nullable=False)
    diagnosis = db.Column(db.Text)
    
    worker = db.relationship("Worker", back_populates="medical_visits")
    facility = db.relationship("HealthcareFacility", back_populates="medical_visits")

class Vaccination(db.Model):
    __tablename__ = "vaccinations"
    id = db.Column(db.Integer, primary_key=True)
    #e worker_id non-nullable.
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"), nullable=False)
    vaccine_name = db.Column(db.String(100), nullable=False)
    dose_number = db.Column(db.Integer, default=1)
    date_administered = db.Column(db.Date, nullable=False)

    worker = db.relationship("Worker", back_populates="vaccinations")