import enum
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db

# Enums 
class GenderEnum(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class UserRoleEnum(enum.Enum):
    ADMIN = "admin"
    HEALTH_OFFICIAL = "health_official"
    NORMAL_USER = "normal_user"

#  User (account) 
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(Enum(UserRoleEnum), default=UserRoleEnum.NORMAL_USER, nullable=False)

    # 1:1 link to Worker (account holder profile)
    worker = db.relationship("Worker", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#  Worker (profile) 
class Worker(db.Model):
    __tablename__ = "workers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)  # 1:1 with User
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(Enum(GenderEnum))
    phone = db.Column(db.String(20))
    access_to_clean_water = db.Column(db.boolean())

    user = db.relationship("User", back_populates="worker")
    health_records = db.relationship("HealthRecord", back_populates="worker")
    medical_visits = db.relationship("MedicalVisit", back_populates="worker")
    vaccinations = db.relationship("Vaccination", back_populates="worker")

#  Healthcare Facility 
class HealthcareFacility(db.Model):
    __tablename__ = "healthcare_facilities"
    id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(150))
    facility_type = db.Column(db.String(100))
    location_city = db.Column(db.String(100))

#  Health Record 
class HealthRecord(db.Model):
    __tablename__ = "health_records"
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)

    worker = db.relationship("Worker", back_populates="health_records")

#  Medical Visit 
class MedicalVisit(db.Model):
    __tablename__ = "medical_visits"
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"))
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
