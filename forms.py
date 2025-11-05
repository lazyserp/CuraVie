from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, TextAreaField, DateField, FloatField
# Added EqualTo, Regexp
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NumberRange, Optional
from wtforms import ValidationError
from models import (
    User, Worker, HealthcareFacility,UserRoleEnum,
    GenderEnum, OccupationEnum, FrequencyEnum, DietTypeEnum,
    PPEUsageEnum, PhysicalStrainEnum, AccommodationEnum, SanitationEnum,
    HearingResultEnum, PositiveNegativeEnum, NormalAbnormalEnum,
    FitnessStatusEnum, CheckupTypeEnum
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
    role = SelectField(
        "I want to sign up as",
        choices=[
            (UserRoleEnum.NORMAL_USER.name, "Worker"),
            (UserRoleEnum.HEALTH_OFFICIAL.name, "Healthcare Facility")
        ],
        validators=[DataRequired()],
        default=UserRoleEnum.NORMAL_USER.name
    )
    # Facility details (only shown/required if role is HEALTH_OFFICIAL)
    facility_name = StringField('Facility Name (Hospital/Clinic)', validators=[Optional(), Length(max=255)])
    facility_type = StringField('Facility Type (e.g., Hospital, Clinic, CHC)', validators=[Optional(), Length(max=100)])
    facility_license_number = StringField('License Number', validators=[Optional(), Length(max=100)])
    facility_address = StringField('Address', validators=[Optional(), Length(max=255)])
    facility_city = StringField('City', validators=[Optional(), Length(max=100)])
    terms = BooleanField("I agree to the Terms", validators=[DataRequired(message="Please accept the terms")])
    submit = SubmitField("Create Account")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken. Choose another.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered. Did you forget your password?')
    
    def validate_facility_name(self, field):
        if self.role.data == UserRoleEnum.HEALTH_OFFICIAL.name and not field.data:
            raise ValidationError('Facility name is required for healthcare facilities.')
    
    def validate_facility_license_number(self, field):
        if self.role.data == UserRoleEnum.HEALTH_OFFICIAL.name:
            if not field.data:
                raise ValidationError('License number is required for healthcare facilities.')
            # Check for duplicate license numbers
            existing = HealthcareFacility.query.filter_by(facility_license_number=field.data.strip()).first()
            if existing:
                raise ValidationError('A facility with this license number already exists.')

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    user_type = SelectField(
        "Login as",
        choices=[
            ("", "Select account type"),
            ("worker", "Worker"),
            ("facility", "Healthcare Facility")
        ],
        validators=[Optional()],
        default=""
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


# --- NEW FORM ADDED HERE ---
class HospitalRegisterWorkerForm(FlaskForm):
    # Key User/Worker fields
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone Number', 
                        validators=[
                            DataRequired(), 
                            Length(min=10, max=20),
                            Regexp(r'^[0-9+]+$', message="Use digits and + only")
                        ])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=14, max=120)])
    gender = SelectField('Gender', choices=[(g.value, g.name.title()) for g in GenderEnum], 
                         validators=[DataRequired()])
    home_state = StringField('Home State', validators=[Optional(), Length(max=100)])

    # Key Occupational field
    occupation = SelectField('Primary Occupation', 
                             choices=[(o.value, o.name.title().replace('_', ' ')) for o in OccupationEnum], 
                             validators=[DataRequired()])
    
    # New User Account fields
    password = PasswordField("Set Default Password", 
                             validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm Default Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")]
    )
    submit = SubmitField("Register Worker")

    def validate_phone(self, phone):
        # Check if phone is already used for a worker profile
        if Worker.query.filter_by(phone=phone.data).first():
            raise ValidationError('A worker with this phone number is already registered.')
        
        # Check if phone is already used as a username
        if User.query.filter_by(username=phone.data).first():
            raise ValidationError('This phone number is already in use as a username.')
# --- END OF NEW FORM ---


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


## HealthRecordForm removed; replaced by MedicalCheckupForm

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


class MedicalCheckupForm(FlaskForm):
    date_of_checkup = DateField('Date of Checkup', format='%Y-%m-%d', validators=[DataRequired()])
    height_cm = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=50, max=250)])
    weight_kg = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=10, max=300)])
    bmi = FloatField('BMI', validators=[Optional(), NumberRange(min=5, max=80)])
    blood_pressure_systolic = IntegerField('BP Systolic', validators=[Optional(), NumberRange(min=50, max=250)])
    blood_pressure_diastolic = IntegerField('BP Diastolic', validators=[Optional(), NumberRange(min=30, max=150)])
    pulse_rate = IntegerField('Pulse Rate (bpm)', validators=[Optional(), NumberRange(min=20, max=220)])
    temperature_celsius = FloatField('Temperature (°C)', validators=[Optional(), NumberRange(min=30, max=45)])
    vision_left = StringField('Vision Left', validators=[Optional(), Length(max=50)])
    vision_right = StringField('Vision Right', validators=[Optional(), Length(max=50)])
    hearing_test_result = SelectField('Hearing', choices=[(e.value, e.name.title()) for e in HearingResultEnum], validators=[Optional()])
    respiratory_rate = IntegerField('Respiratory Rate', validators=[Optional(), NumberRange(min=5, max=80)])
    oxygen_saturation = IntegerField('SpO2 (%)', validators=[Optional(), NumberRange(min=50, max=100)])
    checkup_type = SelectField('Checkup Type', choices=[(c.value, c.name.title().replace('_', ' ')) for c in CheckupTypeEnum], validators=[Optional()])
    geo_location = StringField('Geo Location', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save Checkup')


class LabResultsForm(FlaskForm):
    hemoglobin_g_dl = FloatField('Hemoglobin (g/dL)', validators=[Optional(), NumberRange(min=1, max=25)])
    blood_sugar_fasting = FloatField('Fasting Sugar (mg/dL)', validators=[Optional(), NumberRange(min=20, max=500)])
    blood_sugar_postprandial = FloatField('Postprandial Sugar (mg/dL)', validators=[Optional(), NumberRange(min=20, max=700)])
    cholesterol_total = FloatField('Total Cholesterol (mg/dL)', validators=[Optional(), NumberRange(min=50, max=500)])
    triglycerides = FloatField('Triglycerides (mg/dL)', validators=[Optional(), NumberRange(min=20, max=1000)])
    hdl_cholesterol = FloatField('HDL (mg/dL)', validators=[Optional(), NumberRange(min=1, max=200)])
    ldl_cholesterol = FloatField('LDL (mg/dL)', validators=[Optional(), NumberRange(min=1, max=400)])
    hiv_test_result = SelectField('HIV', choices=[(e.value, e.name.title()) for e in PositiveNegativeEnum], validators=[Optional()])
    hepatitis_b_result = SelectField('Hepatitis B', choices=[(e.value, e.name.title()) for e in PositiveNegativeEnum], validators=[Optional()])
    hepatitis_c_result = SelectField('Hepatitis C', choices=[(e.value, e.name.title()) for e in PositiveNegativeEnum], validators=[Optional()])
    tuberculosis_screening_result = SelectField('Tuberculosis', choices=[(e.value, e.name.title()) for e in PositiveNegativeEnum], validators=[Optional()])
    malaria_test_result = SelectField('Malaria', choices=[(e.value, e.name.title()) for e in PositiveNegativeEnum], validators=[Optional()])
    urine_test_result = SelectField('Urine Test', choices=[(e.value, e.name.title()) for e in NormalAbnormalEnum], validators=[Optional()])
    xray_chest_result = SelectField('Chest X-ray', choices=[(e.value, e.name.title()) for e in NormalAbnormalEnum], validators=[Optional()])
    ecg_result = SelectField('ECG', choices=[(e.value, e.name.title()) for e in NormalAbnormalEnum], validators=[Optional()])
    submit = SubmitField('Save Lab Results')


class DoctorEvaluationForm(FlaskForm):
    doctor_name = StringField('Doctor Name', validators=[Optional(), Length(max=255)])
    doctor_registration_number = StringField('Doctor Registration Number', validators=[Optional(), Length(max=120)])
    general_physical_findings = TextAreaField('General Physical Findings', validators=[Optional()])
    diagnosis = TextAreaField('Diagnosis', validators=[Optional()])
    recommendations = TextAreaField('Recommendations', validators=[Optional()])
    fitness_status = SelectField('Fitness Status', choices=[(e.value, e.name.title().replace('_', ' ')) for e in FitnessStatusEnum], validators=[Optional()])
    follow_up_required = BooleanField('Follow-up Required')
    follow_up_date = DateField('Follow-up Date', format='%Y-%m-%d', validators=[Optional()])
    signature_of_doctor = StringField('Signature (name/file id)', validators=[Optional(), Length(max=255)])
    report_generated_by = StringField('Report Generated By', validators=[Optional(), Length(max=120)])
    report_verified_by = StringField('Report Verified By', validators=[Optional(), Length(max=120)])
    remarks = TextAreaField('Remarks', validators=[Optional()])
    submit = SubmitField('Save Doctor Evaluation')


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