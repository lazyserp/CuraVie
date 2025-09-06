# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NumberRange
from wtforms import ValidationError
# FIX: Import your Enum classes from models to use them in the form
from models import User, GenderEnum, OccupationEnum, FrequencyEnum, DietTypeEnum

class SignUpForm(FlaskForm):
    # ... (No changes needed in this form)
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
    # ... (No changes needed in this form)
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")

class WorkerDetails(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=32), Regexp(r"^[a-zA-Z]+$", message="Only letters are allowed.")])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=1, max=120)])
    age = IntegerField("Age", validators=[DataRequired(), NumberRange(min=16, max=100, message="Please enter a valid age.")])
    phone = StringField("Phone Number", validators=[DataRequired(), Regexp(r'^\+?\d{10,15}$', message="Please enter a valid phone number.")]) 
    access_to_clean_water = BooleanField("Access to Clean Water")
    home_state = StringField("Home State", validators=[DataRequired()])

    # --- ENUM-BASED FIELDS ---
    # FIX: Changed to SelectField and dynamically created choices from the Enum.
    # The `choices` are tuples of (value, label). e.g., ('Male', 'Male')
    gender = SelectField("Gender", choices=[(g.value, g.name.title()) for g in GenderEnum], validators=[DataRequired()])
    
    # FIX: Changed from StringField to a dropdown for data consistency.
    occupation = SelectField("Occupation", choices=[(o.value, o.name.replace('_', ' ').title()) for o in OccupationEnum], validators=[DataRequired()])
    
    work_hours_per_day = IntegerField("Typical Work Hours per Day", validators=[DataRequired(), NumberRange(min=1, max=20)])
    
    # FIX: Changed from BooleanField to a dropdown to capture frequency.
    smoking_habit = SelectField("Smoking Habit", choices=[(f.value, f.name.title()) for f in FrequencyEnum], validators=[DataRequired()])
    
    # FIX: Corrected typo 'alochol' and changed from BooleanField to a dropdown.
    alcohol_consumption = SelectField("Alcohol Consumption", choices=[(f.value, f.name.title()) for f in FrequencyEnum], validators=[DataRequired()])
    
    # FIX: Changed from StringField to a dropdown.
    diet_type = SelectField("Diet Type", choices=[(d.value, d.name.replace('_', ' ').title()) for d in DietTypeEnum], validators=[DataRequired()])
    
    submit = SubmitField("Save Details")