from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NumberRange
from datetime import date
from wtforms import ValidationError
from models import User, GenderEnum, OccupationEnum, FrequencyEnum, DietTypeEnum, Worker
from flask_login import current_user
from database import db
from sqlalchemy import select


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

class WorkerDetails(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    home_state = StringField('Home State', validators=[DataRequired(), Length(max=100)])
    
    # For Enum fields, 'choices' are populated from the Enum itself
    gender = SelectField('Gender', choices=[(g.value, g.name.title()) for g in GenderEnum], validators=[DataRequired()])
    occupation = SelectField('Occupation', choices=[(o.value, o.name.title().replace('_', ' ')) for o in OccupationEnum], validators=[DataRequired()])
    
    work_hours_per_day = IntegerField('Work Hours Per Day', validators=[DataRequired(), NumberRange(min=0, max=24)])
    access_to_clean_water = BooleanField('Access to Clean Water')

    smoking_habit = SelectField('Smoking Habit', choices=[(f.value, f.name.title()) for f in FrequencyEnum], validators=[DataRequired()])
    alcohol_consumption = SelectField('Alcohol Consumption', choices=[(f.value, f.name.title()) for f in FrequencyEnum], validators=[DataRequired()])
    diet_type = SelectField('Diet Type', choices=[(d.value, d.name.title().replace('_', ' ')) for d in DietTypeEnum], validators=[DataRequired()])

    submit = SubmitField('Save Details')

    def validate_phone(self, phone):
            # If the user is editing and their phone number hasn't changed, we don't need to do anything.
            if current_user.worker and current_user.worker.phone == phone.data:
                return

            # In all other cases (creating a new user OR editing to a new number),
            # we must check if the new phone number is already in the database.
            statement = select(Worker).filter_by(phone=phone.data)
            worker_with_phone = db.session.scalar(statement)
            if worker_with_phone:
                raise ValidationError('That phone number is already registered. Please use a different one.')


# STEP 1:
# define your form here , look above classes and see how a form class is generated with reference to its model class.
class HealthRecord(FlaskForm):
    record_date= DateField('Record Date',format='%d-%m-%y',validators=[DataRequired()])
    height_cm=FloatField('Height(cm)',validators=[DataRequired(),NumberRange(min=50,max=300)])
    weight_kg=FloatField('Weight(kg)',validators=[DataRequired(),NumberRange(min=50,max=300)])
    blood_pressure_systolic=IntegerField('Systolic BP(mmHG)', validators=[DataRequired(),NumberRange(min=50,max=250)])
    blood_pressure_diastolic=IntegerField('Diastolic BP(mmHG)', validators=[DataRequired(),NumberRange(min=30,max=150)])
    any_chronic_disease=StringField('Any Chronic Disease')
    submit = SubmitField('Save Details')
    
    def validate_record_date(self,field):
        if field.data>=date.today():
            raise ValidationError('Future Date are not acceptabel')
    
    def validate_blood_pressure_systolic(self,field):
        if self.blood_pressure_diastolic.data and field.data <= self.blood_pressure_diastolic.data:
            raise ValidationError('Systolic BP must be greater than diastolic BP.')


class HealthcareFacilityForm(FlaskForm):
    facility_name = StringField('Facility Name:', validators=[DataRequired(), Length(max=100)])
    facility_type = StringField('Facility Type eg: Clinic , hospital, CHC:', validators=[DataRequired(), Length(max=100)])
    facility_license_number = StringField('Facility License Number', validators=[DataRequired(), Length(max=100)])
    facility_address = StringField('Facility Address', validators=[DataRequired(), Length(max=100)])
    facility_city = StringField('Facility City', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Details')