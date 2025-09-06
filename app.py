import os
from flask import Flask, render_template, redirect, flash, request, url_for
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm

# Import db and models 
from database import db
from models import User, Worker, GenderEnum, OccupationEnum, FrequencyEnum, DietTypeEnum
from forms import SignUpForm, LoginForm, WorkerDetails

# App Initilisation
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

# Authentication routes
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

# --- Fill Details route ---
@app.route("/worker-details", methods=["GET", "POST"])
@login_required
def worker_details():
    # Prevent user from re-filling details if they already exist
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

            #  Convert string data from the form back into Enum objects
            # before saving to the database.
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
        
    return render_template('worker_details.html.j2', form=form)


@app.route("/edit-details", methods=["GET", "POST"])
@login_required
def edit_details():
    # Fetch the worker profile linked to the currently logged-in user.
    worker = current_user.worker
    
    # If the user has no profile yet, redirect them to the creation page.
    if not worker:
        flash("You need to create your profile first.", "warning")
        return redirect(url_for('worker_details'))

    # Pre-populate the form with the worker's existing data using obj=worker.
    form = WorkerDetails(obj=worker)

    # When the user submits the edited form...
    if form.validate_on_submit():
        # Update the existing worker object with the new data from the form.
        worker.first_name = form.first_name.data
        worker.last_name = form.last_name.data
        worker.age = form.age.data
        worker.phone = form.phone.data
        worker.access_to_clean_water = form.access_to_clean_water.data
        worker.home_state = form.home_state.data
        worker.work_hours_per_day = form.work_hours_per_day.data

        # Convert string values from the form back into Enum objects.
        worker.gender = GenderEnum(form.gender.data)
        worker.occupation = OccupationEnum(form.occupation.data)
        worker.smoking_habit = FrequencyEnum(form.smoking_habit.data)
        worker.alcohol_consumption = FrequencyEnum(form.alcohol_consumption.data)
        worker.diet_type = DietTypeEnum(form.diet_type.data)

        # Commit the changes to the database.
        # No need for db.session.add() because the worker object is already in the session.
        db.session.commit()

        flash("Your details have been updated successfully!", "success")
        return redirect(url_for('dashboard'))

    # For a GET request, show the pre-populated form.
    return render_template('worker_details.html.j2', form=form, page_title="Edit Your Details")



# ... (Main Execution is unchanged) ...
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/checked.")
    app.run(debug=True) 