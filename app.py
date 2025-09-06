import os
from flask import Flask, render_template, redirect, flash, request, url_for
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from sqlalchemy import select

# Import db and models 
from database import db
from models import User, Worker, GenderEnum, OccupationEnum, FrequencyEnum, DietTypeEnum
from forms import SignUpForm, LoginForm, WorkerDetails

# App Initialization
class EmptyForm(FlaskForm):
    pass

load_dotenv()
app = Flask(__name__)
csrf = CSRFProtect(app)

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- CONTEXT PROCESSOR ---
# This makes the 'logout_form' available in all templates, so the logout button in the header always works.
@app.context_processor
def inject_forms():
    return dict(logout_form=EmptyForm())

# --- AUTHENTICATION ROUTES ---

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
            flash("That username or email is already taken.", "error")
    # **IMPROVEMENT**: Flash detailed errors if validation fails on POST request
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').title()}: {error}", 'error')
                
    return render_template("signup.html.j2", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    
    if current_user.is_authenticated:
        statement = select(User).filter_by(username=form.username.data.strip())
        user = db.session.scalar(statement)
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page or url_for('dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "error")
    # **IMPROVEMENT**: Flash detailed errors if validation fails on POST request
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').title()}: {error}", 'error')

    return render_template('login.html.j2', form=form)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))

# --- CORE APP ROUTES ---

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html.j2') 

@app.route("/dashboard")
@login_required
def dashboard():
    # No need to pass a form here anymore, the context processor handles it
    return render_template('dashboard.html.j2')

@app.route("/worker-details", methods=["GET", "POST"])
@login_required
def worker_details():
    if current_user.worker:
        flash("You have already filled in your details.", "info")
        return redirect(url_for('dashboard'))

    form = WorkerDetails()
    if form.validate_on_submit():
        worker = Worker(
            user_id=current_user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            age=form.age.data,
            phone=form.phone.data,
            access_to_clean_water=form.access_to_clean_water.data,
            work_hours_per_day=form.work_hours_per_day.data,
            home_state=form.home_state.data,
            gender=GenderEnum(form.gender.data),
            occupation=OccupationEnum(form.occupation.data),
            smoking_habit=FrequencyEnum(form.smoking_habit.data),
            alcohol_consumption=FrequencyEnum(form.alcohol_consumption.data),
            diet_type=DietTypeEnum(form.diet_type.data)
        )
        db.session.add(worker)
        db.session.commit()
        flash("Your details have been saved successfully!", "success")
        return redirect(url_for('dashboard'))
        
    return render_template('worker_details.html.j2', form=form, page_title="Worker Details")
@app.route("/edit-details", methods=["GET", "POST"])
@login_required
def edit_details():
    worker = current_user.worker
    if not worker:
        flash("You need to create your profile first.", "warning")
        return redirect(url_for('worker_details'))

    # The form is pre-populated with the worker's existing data
    form = WorkerDetailsForm(obj=worker)

    if form.validate_on_submit():
        # This handy function updates the 'worker' object with form data
        form.populate_obj(worker)
        
        # We still need to handle Enums manually
        worker.gender = GenderEnum(form.gender.data)
        worker.occupation = OccupationEnum(form.occupation.data)
        worker.smoking_habit = FrequencyEnum(form.smoking_habit.data)
        worker.alcohol_consumption = FrequencyEnum(form.alcohol_consumption.data)
        worker.diet_type = DietTypeEnum(form.diet_type.data)

        db.session.commit()
        flash("Your details have been updated successfully!", "success")
        return redirect(url_for('dashboard'))
    
    # **THIS IS THE FIX**: If validation fails, flash the specific errors
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').title()}: {error}", 'error')

    return render_template('worker_details.html.j2', form=form, page_title="Edit Your Details")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)