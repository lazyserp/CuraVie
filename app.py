import os
from flask import Flask, render_template, redirect, flash, request, url_for, abort
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from sqlalchemy import select
from sqlalchemy.exc import OperationalError 

# --- Import db, models, and forms ---
# I have added all the new models and forms we created.
from database import db
from models import (
    User, Worker, HealthcareFacility, HealthRecord, ActivityLog, Vaccination, MedicalVisit,
    ChronicDiseaseEnum, UserRoleEnum, GenderEnum, OccupationEnum, FrequencyEnum, DietTypeEnum,
    PPEUsageEnum, PhysicalStrainEnum, AccommodationEnum, SanitationEnum
)
from forms import (
    SignUpForm, LoginForm, WorkerDetailsForm, HealthcareFacilityForm,
    HealthRecordForm, ActivityLogForm, VaccinationForm, MedicalVisitForm
)

# --- App Initialization ---

# An empty form is used for the logout button which doesn't need any fields.
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

# This makes the 'logout_form' available in all templates
@app.context_processor
def inject_forms():
    return dict(logout_form=EmptyForm())



# --- AUTHENTICATION ROUTES (Unchanged) ---

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.strip(), email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            flash("That username or email is already taken.", "error")
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.replace('_', ' ').title()}: {error}", 'error')
    return render_template("signup.html.j2", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
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
    return redirect(url_for("home"))

# --- CORE APP ROUTES ---

@app.route("/")
def home():
    return render_template('index.html.j2') 

@app.route("/dashboard")
@login_required
def dashboard():
    # You can pass the worker object to the template to display their info
    worker = current_user.worker
    return render_template('dashboard.html.j2', worker=worker)

# --- Worker Profile Routes (UPDATED) ---

@app.route("/create-profile", methods=["GET", "POST"])
@login_required
def worker_details():
    if current_user.worker:
        flash("You have already created your profile. You can edit it instead.", "info")
        return redirect(url_for('dashboard'))

    form = WorkerDetailsForm()
    if form.validate_on_submit():
        # UPDATED: Now includes all the new fields from the detailed form
        worker = Worker(
            user_id=current_user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            age=form.age.data,
            phone=form.phone.data,
            home_state=form.home_state.data,
            gender=GenderEnum(form.gender.data),
            # Occupational
            occupation=OccupationEnum(form.occupation.data),
            work_hours_per_day=form.work_hours_per_day.data,
            physical_strain=PhysicalStrainEnum(form.physical_strain.data),
            ppe_usage=PPEUsageEnum(form.ppe_usage.data),
            # Lifestyle
            smoking_habit=FrequencyEnum(form.smoking_habit.data),
            alcohol_consumption=FrequencyEnum(form.alcohol_consumption.data),
            diet_type=DietTypeEnum(form.diet_type.data),
            meals_per_day=form.meals_per_day.data,
            junk_food_frequency=FrequencyEnum(form.junk_food_frequency.data),
            sleep_hours_per_night=form.sleep_hours_per_night.data,
            # Living Conditions
            accommodation_type=AccommodationEnum(form.accommodation_type.data),
            sanitation_quality=SanitationEnum(form.sanitation_quality.data),
            access_to_clean_water=form.access_to_clean_water.data,
            # Mental Health
            stress_level=form.stress_level.data,
            has_social_support=form.has_social_support.data
        )
        db.session.add(worker)
        db.session.commit()
        flash("Your profile has been created successfully!", "success")
        return redirect(url_for('dashboard'))
    elif request.method == 'POST':
        flash("Please correct the errors below.", "error")
        
    return render_template('worker_details.html.j2', form=form, page_title="Create Your Profile")

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_details():
    worker = current_user.worker
    if not worker:
        flash("You need to create your profile first.", "warning")
        return redirect(url_for('worker_details'))

    form = WorkerDetailsForm(obj=worker)
    if form.validate_on_submit():
        # UPDATED: populate_obj updates most fields automatically
        form.populate_obj(worker)
        
        # Manually update all the Enum fields
        worker.gender = GenderEnum(form.gender.data)
        worker.occupation = OccupationEnum(form.occupation.data)
        worker.physical_strain = PhysicalStrainEnum(form.physical_strain.data)
        worker.ppe_usage = PPEUsageEnum(form.ppe_usage.data)
        worker.smoking_habit = FrequencyEnum(form.smoking_habit.data)
        worker.alcohol_consumption = FrequencyEnum(form.alcohol_consumption.data)
        worker.diet_type = DietTypeEnum(form.diet_type.data)
        worker.junk_food_frequency = FrequencyEnum(form.junk_food_frequency.data)
        worker.accommodation_type = AccommodationEnum(form.accommodation_type.data)
        worker.sanitation_quality = SanitationEnum(form.sanitation_quality.data)

        db.session.commit()
        flash("Your profile has been updated successfully!", "success")
        return redirect(url_for('dashboard'))
    elif request.method == 'POST':
        flash("Please correct the errors below.", "error")

    return render_template('worker_details.html.j2', form=form, page_title="Edit Your Profile")


# --- NEW ROUTES FOR HEALTH DATA ---
# In app.py
@app.route("/add-health-record", methods=["GET", "POST"])
@login_required
def add_health_record():
    worker = current_user.worker
    if not worker:
        flash("Please create your profile before adding health records.", "warning")
        return redirect(url_for('worker_details'))
    
    form = HealthRecordForm()
    if form.validate_on_submit():
        health_record = HealthRecord(
            worker_id=worker.id,
            height_cm=form.height_cm.data,
            weight_kg=form.weight_kg.data,
            blood_pressure_systolic=form.blood_pressure_systolic.data,
            blood_pressure_diastolic=form.blood_pressure_diastolic.data,
        )
        
        # Convert the list of selected diseases into a single comma-separated string
        diseases_list = form.chronic_diseases.data
        worker.chronic_diseases = ",".join(diseases_list) if diseases_list else None # Use None for empty
        
        db.session.add(health_record)
        db.session.commit()
        flash("Health record added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('health_Record.html.j2', form=form, page_title="Add Health Record")

@app.route("/log-activity", methods=["GET", "POST"])
@login_required
def log_activity():
    if not current_user.worker:
        flash("Please create your profile first.", "warning")
        return redirect(url_for('worker_details'))
        
    form = ActivityLogForm()
    if form.validate_on_submit():
        activity = ActivityLog(
            worker_id=current_user.worker.id,
            activity_type=form.activity_type.data,
            duration_minutes=form.duration_minutes.data,
            notes=form.notes.data
        )
        db.session.add(activity)
        db.session.commit()
        flash("Activity logged successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('log_activity.html.j2', form=form)

@app.route("/add-vaccination", methods=["GET", "POST"])
@login_required
def add_vaccination():
    if not current_user.worker:
        flash("Please create your profile first.", "warning")
        return redirect(url_for('worker_details'))

    form = VaccinationForm()
    if form.validate_on_submit():
        vaccination = Vaccination(
            worker_id=current_user.worker.id,
            vaccine_name=form.vaccine_name.data,
            dose_number=form.dose_number.data,
            date_administered=form.date_administered.data
        )
        db.session.add(vaccination)
        db.session.commit()
        flash("Vaccination record added!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_vaccination.html.j2', form=form)

# --- Routes for Health Officials ---

@app.route("/register-facility", methods=["GET","POST"])
@login_required
def register_facility():
    # Optional: You can restrict this page to certain user roles
    if current_user.role != UserRoleEnum.HEALTH_OFFICIAL:
        flash("You do not have permission to register a facility.", "error")
        return redirect(url_for('dashboard'))

    form = HealthcareFacilityForm()
    if form.validate_on_submit():
        facility = HealthcareFacility(
            registered_by_user_id=current_user.id,
            facility_name = form.facility_name.data,
            facility_type = form.facility_type.data,
            facility_license_number = form.facility_license_number.data,
            facility_address = form.facility_address.data,
            facility_city = form.facility_city.data
        )
        db.session.add(facility)
        db.session.commit()
        flash("Healthcare facility registered successfully!", "success")
        return redirect(url_for('dashboard'))
        
    return render_template('healthcare_facility.html.j2', form=form, page_title="Register Facility")

@app.route("/worker/<int:worker_id>/add-medical-visit", methods=["GET", "POST"])
@login_required
def add_medical_visit(worker_id):
    # This route is intended for health officials to add records for workers.
    if current_user.role != UserRoleEnum.HEALTH_OFFICIAL:
        abort(403) # Forbidden access

    worker = Worker.query.get_or_404(worker_id)
    form = MedicalVisitForm()

    if form.validate_on_submit():
        visit = MedicalVisit(
            worker_id=worker.id,
            facility_id=form.facility_id.data, # This assumes the official knows their facility ID
            doctor_name=form.doctor_name.data,
            visit_date=form.visit_date.data,
            diagnosis=form.diagnosis.data,
            report_id=form.report_id.data
        )
        db.session.add(visit)
        db.session.commit()
        flash(f"Medical visit for {worker.first_name} has been recorded.", "success")
        return redirect(url_for('dashboard')) # Or redirect to a patient management page

    return render_template('add_medical_visit.html.j2', form=form, worker=worker)

# --- Main Execution ---

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)