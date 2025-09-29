from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NumberRange, Optional
from wtforms import ValidationError
from models import (
    User, Worker, HealthcareFacility,UserRoleEnum,
    GenderEnum, OccupationEnum, FrequencyEnum, DietTypeEnum,
    PPEUsageEnum, PhysicalStrainEnum, AccommodationEnum, SanitationEnum
)
from flask_login import current_user
from database import db 
from sqlalchemy import select
from datetime import date

# User Account Forms 

class SignUpForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=32),
            Regexp(r"^[a-zA-Z0-9_.-]+$", message="Use letters, numbers, _, . or -")
        ]
    )
    email = StringField("Email address", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")]
    )
    terms = BooleanField("I agree to the Terms", validators=[DataRequired(message="Please accept the terms")])
    submit = SubmitField("Create Account")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken. Choose another.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered. Did you forget your password?')

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


# Worker & Health Profile Forms 

class WorkerDetailsForm(FlaskForm):

    # Basic Bio
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[Length(max=100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=14, max=120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    home_state = StringField('Home State (e.g., West Bengal, Bihar)', validators=[DataRequired(), Length(max=100)])
    gender = SelectField('Gender', choices=[(g.value, g.name.title()) for g in GenderEnum], validators=[DataRequired()])

    # Occupational Details
    occupation = SelectField('Primary Occupation', choices=[(o.value, o.name.title().replace('_', ' ')) for o in OccupationEnum], validators=[DataRequired()])
    work_hours_per_day = IntegerField('Average Work Hours Per Day', validators=[DataRequired(), NumberRange(min=1, max=24)])
    physical_strain = SelectField('Physical Strain of Job', choices=[(p.value, p.name.title().replace('_', ' ')) for p in PhysicalStrainEnum], validators=[DataRequired()])
    ppe_usage = SelectField('Use of Safety Gear (PPE)', choices=[(p.value, p.name.title()) for p in PPEUsageEnum], validators=[DataRequired()])

    # Lifestyle & Environment
    smoking_habit = SelectField('Smoking Habit', choices=[(f.value, f.name.title()) for f in FrequencyEnum], validators=[DataRequired()])
    alcohol_consumption = SelectField('Alcohol Consumption', choices=[(f.value, f.name.title()) for f in FrequencyEnum], validators=[DataRequired()])
    diet_type = SelectField('Diet Type', choices=[(d.value, d.name.title().replace('_', ' ')) for d in DietTypeEnum], validators=[DataRequired()])
    meals_per_day = IntegerField('How many meals do you typically eat per day?', validators=[DataRequired(), NumberRange(min=1, max=10)])
    junk_food_frequency = SelectField('Junk Food Consumption', choices=[(f.value, f.name.title()) for f in FrequencyEnum], validators=[DataRequired()])
    sleep_hours_per_night = IntegerField('Average Hours of Sleep per Night', validators=[DataRequired(), NumberRange(min=1, max=16)])

    # Living Conditions
    accommodation_type = SelectField('Current Accommodation', choices=[(a.value, a.name.title().replace('_', ' ')) for a in AccommodationEnum], validators=[DataRequired()])
    sanitation_quality = SelectField('Toilet Facility Type', choices=[(s.value, s.name.title().replace('_', ' ')) for s in SanitationEnum], validators=[DataRequired()])
    access_to_clean_water = BooleanField('Do you have reliable access to clean drinking water?')

    # Mental Health
    stress_level = IntegerField('On a scale of 1 to 10, what is your current stress level?', validators=[DataRequired(), NumberRange(min=1, max=10)])
    has_social_support = BooleanField('Do you have friends or family nearby for support?')

    submit = SubmitField('Save Profile')

    def validate_phone(self, phone):
        # Prevent duplicate phone numbers
        if current_user.worker and current_user.worker.phone == phone.data:
            return
        statement = select(Worker).filter_by(phone=phone.data)
        worker_with_phone = db.session.scalar(statement)
        if worker_with_phone:
            raise ValidationError('This phone number is already registered.')


class HealthRecordForm(FlaskForm):
    record_date= DateField('Record Date',format='%Y-%m-%d',validators=[DataRequired()])
    height_cm = IntegerField('Height (cm)', validators=[DataRequired(), NumberRange(min=50, max=250)])
    weight_kg = IntegerField('Weight (kg)', validators=[DataRequired(), NumberRange(min=10, max=300)])
    blood_pressure_systolic = IntegerField('Blood Pressure (Systolic)', validators=[DataRequired(), NumberRange(min=50, max=250)])
    blood_pressure_diastolic = IntegerField('Blood Pressure (Diastolic)', validators=[DataRequired(), NumberRange(min=30, max=150)])
    chronic_diseases = StringField('Any Chronic Disease')
    submit = SubmitField('Add Health Record')

    
    def validate_record_date(self,field):
        if field.data > date.today():
            raise ValidationError('Future Date are not acceptable')
    
    def validate_blood_pressure_systolic(self,field):
        if self.blood_pressure_diastolic.data and field.data <= self.blood_pressure_diastolic.data:
            raise ValidationError('Systolic BP must be greater than diastolic BP.')

class MedicalVisitForm(FlaskForm):

    facility_id = IntegerField('Healthcare Facility ID', validators=[DataRequired()])
    doctor_name = StringField('Doctor\'s Name', validators=[DataRequired(), Length(max=255)])
    visit_date = DateField('Date of Visit', format='%Y-%m-%d', validators=[DataRequired()])
    diagnosis = TextAreaField('Diagnosis / Reason for Visit', validators=[DataRequired()])
    report_id = StringField('Report ID (Optional)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Log Medical Visit')

class VaccinationForm(FlaskForm):

    vaccine_name = StringField('Vaccine Name (e.g., COVID-19, Tetanus)', validators=[DataRequired(), Length(max=100)])
    dose_number = IntegerField('Dose Number', validators=[DataRequired(), NumberRange(min=1)])
    date_administered = DateField('Date Administered', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add Vaccination')

class ActivityLogForm(FlaskForm):
    
    activity_type = StringField('Activity Type (e.g., Walking, Manual Labor)', validators=[DataRequired(), Length(max=100)])
    duration_minutes = IntegerField('Duration (in minutes)', validators=[DataRequired(), NumberRange(min=1)])
    notes = TextAreaField('Notes (Optional)')
    submit = SubmitField('Log Activity')


# Healthcare Facility Form 

class HealthcareFacilityForm(FlaskForm):
    facility_name = StringField('Facility Name:', validators=[DataRequired(), Length(max=100)])
    facility_type = StringField('Facility Type eg: Clinic , hospital, CHC:', validators=[DataRequired(), Length(max=100)])
    facility_license_number = StringField('Facility License Number', validators=[DataRequired(), Length(max=100)])
    facility_address = StringField('Facility Address', validators=[DataRequired(), Length(max=100)])
    facility_city = StringField('Facility City', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Register Facility')



class AdminAddUserForm(FlaskForm):
    username = StringField(
    "Username",
    validators=[
        DataRequired(),
        Length(min=3, max=32),
        Regexp(r"^[a-zA-Z0-9_.-]+$", message="Use letters, numbers, _, . or -")])
    email = StringField("Email address", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    role = SelectField("Role",choices=[(role.name, role.value) for role in UserRoleEnum])
    submit = SubmitField('Add User')

