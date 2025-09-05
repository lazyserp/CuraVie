# models.py (Enhanced Version)
import enum
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db

# --- Enums ---
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

# --- Models ---

class User(db.Model):
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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    
    # Basic Bio
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(Enum(GenderEnum), nullable=False)
    phone = db.Column(db.String(20))
    preferred_language = db.Column(db.String(50), default='Hindi') # For AI output

    # Occupational Data 
    occupation = db.Column(Enum(OccupationEnum), nullable=False)
    work_hours_per_day = db.Column(db.Integer)
    years_in_occupation = db.Column(db.Integer)
    is_migrant = db.Column(db.Boolean, default=True)
    home_state = db.Column(db.String(100)) # e.g., West Bengal, Bihar

    # Lifestyle & Habits 
    smoking_habit = db.Column(Enum(FrequencyEnum), default=FrequencyEnum.NEVER)
    alcohol_consumption = db.Column(Enum(FrequencyEnum), default=FrequencyEnum.NEVER)
    diet_type = db.Column(Enum(DietTypeEnum))
    access_to_clean_water = db.Column(db.Boolean, default=True)
    housing_condition = db.Column(db.String(255)) # e.g., 'Shared dormitory', 'Site hut'

    # Relationships
    user = db.relationship("User", back_populates="worker")
    health_records = db.relationship("HealthRecord", back_populates="worker", cascade="all, delete-orphan")
    medical_visits = db.relationship("MedicalVisit", back_populates="worker", cascade="all, delete-orphan")
    vaccinations = db.relationship("Vaccination", back_populates="worker", cascade="all, delete-orphan")

class HealthRecord(db.Model):
    __tablename__ = "health_records"
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"))
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Physical Metrics
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    blood_sugar_level = db.Column(db.Float) # Fasting or random
    any_chronic_disease = db.Column(db.String(100))

    worker = db.relationship("Worker", back_populates="health_records")

#  Medical Visit 
class MedicalVisit(db.Model):
    __tablename__ = "medical_visits"
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id")) #report id for offline assessments
    facility_id = db.Column(db.Integer, db.ForeignKey("healthcare_facilities.id"))
    visit_date = db.Column(db.Date)
    diagnosis = db.Column(db.Text)

    worker = db.relationship("Worker", back_populates="medical_visits")
    facility = db.relationship("HealthcareFacility")

#  Vaccination 
class Vaccination(db.Model):
    __tablename__ = "vaccinations"
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"))
    vaccine_name = db.Column(db.String(100))
    dose_number = db.Column(db.Integer)
    date_administered = db.Column(db.Date)

    worker = db.relationship("Worker", back_populates="vaccinations")
