from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
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