import enum
from sqlalchemy import CheckConstraint, Enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db

# --- Enums for consistent data ---
class GenderEnum(enum.Enum):
    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other'

class UserRoleEnum(enum.Enum):
    ADMIN = 'admin'
    HEALTH_OFFICIAL = 'health_official'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.HEALTH_OFFICIAL)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- NEW: Healthcare Infrastructure Models ---
class HealthcareFacility(db.Model):
    __tablename__ = 'healthcare_facilities'
    id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(150), nullable=False)
    facility_type = db.Column(db.String(100)) # e.g., 'Clinic', 'Hospital'
    location_city = db.Column(db.String(100), nullable=False)

# --- Core Domain Models (Worker and their data) ---
class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(Enum(GenderEnum), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    work_detail = db.relationship('WorkDetail', back_populates='worker', uselist=False, cascade="all, delete-orphan")
    health_records = db.relationship('HealthRecord', back_populates='worker', cascade="all, delete-orphan")
    medical_visits = db.relationship('MedicalVisit', back_populates='worker', cascade="all, delete-orphan")
    vaccinations = db.relationship('Vaccination', back_populates='worker', cascade="all, delete-orphan")

class WorkDetail(db.Model):
    __tablename__ = 'work_details'
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False, unique=True)
    type_of_work = db.Column(db.String(100), nullable=False)
    monthly_income = db.Column(db.Integer)
    worker = db.relationship('Worker', back_populates='work_detail')

class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    is_smoker = db.Column(db.Boolean, default=False)
    is_drinker = db.Column(db.Boolean, default=False)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    worker = db.relationship('Worker', back_populates='health_records')

# --- Expanded Health Data Models ---
class MedicalVisit(db.Model):
    __tablename__ = 'medical_visits'
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    facility_id = db.Column(db.Integer, db.ForeignKey('healthcare_facilities.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    doctor_name = db.Column(db.String(150)) # Simplified from your schema for speed

    worker = db.relationship('Worker', back_populates='medical_visits')
    facility = db.relationship('HealthcareFacility')

class Vaccination(db.Model):
    __tablename__ = 'vaccinations'
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    vaccine_name = db.Column(db.String(100), nullable=False) # e.g., 'COVID-19', 'Tetanus'
    dose_number = db.Column(db.Integer, nullable=False)
    date_administered = db.Column(db.Date, nullable=False)

    worker = db.relationship('Worker', back_populates='vaccinations')