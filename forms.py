from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NumberRange
from wtforms import ValidationError
from models import User

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


<<<<<<< HEAD
    def validate_login(self,field):
        if not User.query.filter((User.username == field.data) | (User.email == field.data.lower())).first():
            raise ValidationError('Email/Username incorrect')
        
class entryform(FlaskForm):
    user_id=IntegerField("user id",validators=[DataRequired(),NumberRange(min=1,max=100)])
    first_name=StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(min=3,max=32),
            Regexp(r"^[a-zA-Z]+$", message="Use letters, numbers, _, . or ")
    ])
    last_name=StringField("Last Name",validators=[DataRequired(),Length(min=3,max=120)])
    age=IntegerField("Age",validators=[DataRequired(),NumberRange(min=10,max=100,message="Enter a Valid Age")])
    gender=SelectField("Gender",choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],validators=[DataRequired()])
    Phone=StringField("Phone Number",validators=[DataRequired(),Regexp(r'^\+?\d{10,15}$',message="Enter a Valid Phone Number")]) 
    access_to_clean_water=BooleanField("Access to Clean Water")
=======
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired())
    password = PasswordField("Password",validators=[DataRequired())
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")
>>>>>>> 76f7402189cf97265bf99187e759ed0117106b79
