# app.py
import os
from flask import Flask, render_template, redirect, flash, request, url_for
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm

# Import db and models
from database import db
from models import User, Worker, HealthRecord, MedicalVisit, Vaccination, HealthcareFacility
from forms import SignUpForm, LoginForm

# App Initialization & Configuration 

class EmptyForm(FlaskForm):
    pass

load_dotenv()
app = Flask(__name__)
csrf = CSRFProtect(app)

# Database and Secret Key Configuration
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

#  Extensions Initialization 

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#  Authentication Routes 

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            # This is a fallback error in case the form validation somehow misses a race condition.
            flash("An unexpected error occurred. That username or email might already be taken.", "danger")

    return render_template("signup.html.j2", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page or url_for('dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "danger")

    return render_template('login.html.j2', form=form)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))

# --- Core Application Routes ---

@app.route("/dashboard")
@login_required
def dashboard():
    form = EmptyForm()
    return render_template('dashboard.html.j2', form=form)

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html.j2') 

# --- Main Execution ---

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/checked.")

    app.run(debug=True)