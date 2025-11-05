import os
from flask import Flask, render_template, redirect, flash, request, url_for, abort, send_file
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import select,func
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
# from sqlalchemy import func
# from datetime import date
from decorators import require_role
from pdf_gen import create_report_pdf

# from io import BytesIO
# from weasyprint import HTML
from ai_service import generate_health_report 


from database import db
from models import (
    User, Worker, HealthcareFacility, ActivityLog, Vaccination, MedicalVisit,
    MedicalCheckup, LabResults, DoctorEvaluation,
    UserRoleEnum, GenderEnum, OccupationEnum, FrequencyEnum, DietTypeEnum,
    PPEUsageEnum, PhysicalStrainEnum, AccommodationEnum, SanitationEnum,
    # Added Enums needed for new route
    HearingResultEnum, CheckupTypeEnum, FitnessStatusEnum, PositiveNegativeEnum, NormalAbnormalEnum
)
from forms import (
    SignUpForm, LoginForm, WorkerDetailsForm, HealthcareFacilityForm,
    ActivityLogForm, VaccinationForm, MedicalVisitForm, AdminAddUserForm,
    MedicalCheckupForm, LabResultsForm, DoctorEvaluationForm,
    # --- NEW FORM IMPORTED ---
    HospitalRegisterWorkerForm
)

# App Initialization 

# An empty form is used for the logout button which doesn't need any fields.
class EmptyForm(FlaskForm):
    pass

load_dotenv()
app = Flask(__name__)
csrf = CSRFProtect(app)



db_user = os.getenv("MYSQLUSER") or os.getenv("DB_USER")
db_pass = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASS")
db_host = os.getenv("MYSQLHOST") or os.getenv("DB_HOST")
db_name = os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME")
db_port = os.getenv("MYSQLPORT")

# Handle empty or missing port safely
if db_port and db_port.strip():
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
#new seettings 

# SQLAlchemy settings
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


#  AUTHENTICATION ROUTES 

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SignUpForm()
    if form.validate_on_submit():
        # Get role from form - security check: only allow NORMAL_USER or HEALTH_OFFICIAL
        role_str = form.role.data
        if role_str not in [UserRoleEnum.NORMAL_USER.name, UserRoleEnum.HEALTH_OFFICIAL.name]:
            flash("Invalid role selected. Admin accounts can only be created by database administrators.", "error")
            return render_template("signup.html.j2", form=form)
        role = UserRoleEnum[role_str]
        user = User(username=form.username.data.strip(), email=form.email.data.strip().lower(), role=role)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.flush()  # Flush to get user.id
            
            # If signing up as healthcare facility, create facility record
            if role == UserRoleEnum.HEALTH_OFFICIAL:
                facility = HealthcareFacility(
                    registered_by_user_id=user.id,
                    facility_name=form.facility_name.data.strip(),
                    facility_type=form.facility_type.data.strip() if form.facility_type.data else None,
                    facility_license_number=form.facility_license_number.data.strip(),
                    facility_address=form.facility_address.data.strip() if form.facility_address.data else None,
                    facility_city=form.facility_city.data.strip() if form.facility_city.data else None
                )
                db.session.add(facility)
            
            db.session.commit()
            role_name = "Healthcare Facility" if role == UserRoleEnum.HEALTH_OFFICIAL else "Worker"
            flash(f"Account created successfully as {role_name}! Please log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError as e:
            db.session.rollback()
            flash("That username or email is already taken, or license number already exists.", "error")
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

@app.route("/admin_dashboard", methods=["GET", "POST"])
@require_role(["admin"])
def admin_dashboard():
    form = AdminAddUserForm()
    facility_form = HealthcareFacilityForm()
    
    # Handle user creation form
    if request.method == 'POST' and form.submit.data:
        if form.validate():
            user = User(username=form.username.data.strip(), email=form.email.data.strip().lower(), role=UserRoleEnum[form.role.data])
            user.set_password(form.password.data)
            try:
                db.session.add(user)
                db.session.commit()
                flash("User created successfully!", "success")
            except IntegrityError:
                db.session.rollback()
                flash("That username or email is already taken.", "error")
            return redirect(url_for('admin_dashboard'))
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field.replace('_', ' ').title()}: {error}", 'error')
    
    # Handle facility creation form
    if request.method == 'POST' and facility_form.submit.data:
        if facility_form.validate():
            new_facility = HealthcareFacility(
                registered_by_user_id=current_user.id if current_user.is_authenticated else 1,
                facility_name=facility_form.facility_name.data.strip(),
                facility_type=facility_form.facility_type.data.strip(),
                facility_license_number=facility_form.facility_license_number.data.strip(),
                facility_address=facility_form.facility_address.data.strip(),
                facility_city=facility_form.facility_city.data.strip()
            )
            try:
                db.session.add(new_facility)
                db.session.commit()
                flash("New healthcare facility added successfully!", "success")
            except IntegrityError:
                db.session.rollback()
                flash("A facility with this license number already exists.", "danger")
            return redirect(url_for("admin_dashboard"))
        else:
            # Form validation failed
            for field, errors in facility_form.errors.items():
                for error in errors:
                    flash(f"{field.replace('_', ' ').title()}: {error}", 'error')
    
    # Handle search query (GET request)
    search_query = request.args.get('search', '').strip()
    search_results = []
    if search_query:
        search_results = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
        if not search_results:
            flash(f"No users found for '{search_query}'.", "warning")
    
    # Get statistics
    no_of_users = db.session.scalar(select(func.count()).select_from(User))
    total_facilities = db.session.scalar(select(func.count()).select_from(HealthcareFacility))
    
    return render_template("admin_dashboard.html.j2",
                           total_users=no_of_users,
                           total_hospitals=total_facilities,
                           form=form,
                           facility_form=facility_form,
                           search_results=search_results,
                           search_query=search_query)

# CORE APP ROUTES 
@app.route("/")
def home():
    return render_template('index.html.j2') 

@app.route("/dashboard")
@login_required
def dashboard():
    # passing worker objetc to the template
    worker = current_user.worker

    if current_user.role == UserRoleEnum.ADMIN:
        return redirect(url_for('admin_dashboard'))
    
    return render_template('dashboard.html.j2', worker=worker)

@app.route("/tos")
def tos():
    return render_template('tos.html')

# Worker Profile Routes 

@app.route("/create-profile", methods=["GET", "POST"])
@login_required
def worker_details():
    if current_user.worker:
        flash("You have already created your profile. You can edit it instead.", "info")
        return redirect(url_for('dashboard'))

    form = WorkerDetailsForm()
    if form.validate_on_submit():
        
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
        # pre filling the details
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



 

@app.route("/log-activity", methods=["GET", "POST"])
@login_required
def log_activity():
    if not current_user.worker:
        flash("Please create your profile first.", "warning")
        return redirect(url_for('worker_details'))
        
    form = ActivityLogForm()

    # Prefill with latest activity on GET
    if request.method == 'GET':
        latest_activity = ActivityLog.query.filter_by(worker_id=current_user.worker.id).order_by(ActivityLog.date.desc()).first()
        if latest_activity:
            if latest_activity.activity_type:
                form.activity_type.data = latest_activity.activity_type
            if latest_activity.duration_minutes is not None:
                form.duration_minutes.data = latest_activity.duration_minutes
            if latest_activity.notes:
                form.notes.data = latest_activity.notes
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
    
    # Prefill with latest vaccination on GET requests
    if request.method == 'GET':
        latest_vaccination = Vaccination.query.filter_by(worker_id=current_user.worker.id).order_by(Vaccination.date_administered.desc()).first()
        if latest_vaccination:
            if latest_vaccination.vaccine_name:
                form.vaccine_name.data = latest_vaccination.vaccine_name
            if latest_vaccination.dose_number is not None:
                form.dose_number.data = latest_vaccination.dose_number
            if latest_vaccination.date_administered:
                form.date_administered.data = latest_vaccination.date_administered
    
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

# Routes for Health Officials 

# --- THIS ROUTE HAS BEEN REMOVED TO AVOID CONFUSION ---
# @app.route("/register-facility", methods=["GET","POST"])
# @login_required
# def register_facility():
#     # Restricting access
#     if current_user.role != UserRoleEnum.HEALTH_OFFICIAL:
#         flash("You do not have permission to register a facility.", "error")
#         return redirect(url_for('dashboard'))
# 
#     form = HealthcareFacilityForm()
#     if form.validate_on_submit():
#         facility = HealthcareFacility(
#             registered_by_user_id=current_user.id,
#             facility_name = form.facility_name.data,
#             facility_type = form.facility_type.data,
#             facility_license_number = form.facility_license_number.data,
#             facility_address = form.facility_address.data,
#             facility_city = form.facility_city.data
#         )
#         db.session.add(facility)
#         db.session.commit()
#         flash("Healthcare facility registered successfully!", "success")
#         return redirect(url_for('dashboard'))
#         
#     return render_template('healthcare_facility.html.j2', form=form, page_title="Register Facility")
# --- END OF REMOVED ROUTE ---


# --- NEW ROUTE FOR FACILITY TO REGISTER A WORKER ---
@app.route("/facility/register-worker", methods=["GET", "POST"])
@require_role(["HEALTH_OFFICIAL", "ADMIN"])
def register_worker_by_facility():
    form = HospitalRegisterWorkerForm()
    if form.validate_on_submit():
        phone = form.phone.data
        
        # Use phone number as username and a placeholder email
        username = phone
        placeholder_email = f"{phone}@placeholder.hospital.com"

        # Check for existing user (double-check, though form validator does it)
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=placeholder_email).first()
        if existing_user or existing_email:
            flash("A user with this phone number or placeholder email already exists.", "error")
            return render_template("register_worker_by_facility.html.j2", form=form)

        try:
            # 1. Create the User
            user = User(
                username=username,
                email=placeholder_email,
                role=UserRoleEnum.NORMAL_USER
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()  # Get the user.id before committing

            # 2. Create the Worker
            worker = Worker(
                user_id=user.id,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                age=form.age.data,
                gender=GenderEnum(form.gender.data),
                home_state=form.home_state.data,
                occupation=OccupationEnum(form.occupation.data)
            )
            db.session.add(worker)
            db.session.commit()
            
            flash(f"Worker {worker.first_name} registered successfully!", "success")
            # Redirect straight to the new worker's medical record page
            return redirect(url_for('view_worker_medical_records', worker_id=worker.id))

        except IntegrityError:
            db.session.rollback()
            flash("An error occurred (e.g., duplicate phone). Please check the details.", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {e}", "error")

    return render_template("register_worker_by_facility.html.j2", form=form)
# --- END OF NEW ROUTE ---


@app.route("/worker/<int:worker_id>/add-medical-visit", methods=["GET", "POST"])
@login_required
def add_medical_visit(worker_id):
    # Restricting access
    if current_user.role != UserRoleEnum.HEALTH_OFFICIAL:
        abort(403) # Forbidden access

    worker = Worker.query.get_or_404(worker_id)
    form = MedicalVisitForm()

    if form.validate_on_submit():
        visit = MedicalVisit(
            worker_id=worker.id,
            facility_id=form.facility_id.data,
            doctor_name=form.doctor_name.data,
            visit_date=form.visit_date.data,
            diagnosis=form.diagnosis.data,
            report_id=form.report_id.data
        )
        db.session.add(visit)
        db.session.commit()
        flash(f"Medical visit for {worker.first_name} has been recorded.", "success")
        return redirect(url_for('dashboard')) 

    return render_template('add_medical_visit.html.j2', form=form, worker=worker)


@app.route("/search-workers", methods=["GET", "POST"])
@require_role(["admin", "health_official"])
def search_workers():
    """Search for workers by name, phone, or ID"""
    search_query = request.args.get('q', '').strip() or (request.form.get('search_query', '').strip() if request.method == 'POST' else '')
    workers = []
    
    if search_query:
        # Search by name, phone, employment_id, or migrant_id_number
        filters = [
            Worker.first_name.ilike(f"%{search_query}%"),
            Worker.last_name.ilike(f"%{search_query}%"),
            Worker.phone.ilike(f"%{search_query}%")
        ]
        # Add optional fields if they exist in the model
        if hasattr(Worker, 'employment_id'):
            filters.append(Worker.employment_id.ilike(f"%{search_query}%"))
        if hasattr(Worker, 'migrant_id_number'):
            filters.append(Worker.migrant_id_number.ilike(f"%{search_query}%"))
        
        workers = Worker.query.filter(db.or_(*filters)).all()
        
        if not workers:
            flash(f"No workers found matching '{search_query}'.", "warning")
    
    return render_template('search_workers.html.j2', workers=workers, search_query=search_query)

@app.route("/worker/<int:worker_id>/medical-records")
@require_role(["admin", "health_official"])
def view_worker_medical_records(worker_id):
    """View all medical records for a specific worker"""
    worker = Worker.query.get_or_404(worker_id)
    
    # Get all medical checkups ordered by date (newest first)
    checkups = MedicalCheckup.query.filter_by(worker_id=worker.id).order_by(MedicalCheckup.date_of_checkup.desc()).all()
    
    # Get all vaccinations
    vaccinations = Vaccination.query.filter_by(worker_id=worker.id).order_by(Vaccination.date_administered.desc()).all()
    
    # Get all medical visits
    medical_visits = MedicalVisit.query.filter_by(worker_id=worker.id).order_by(MedicalVisit.visit_date.desc()).all()
    
    # Get all activity logs
    activity_logs = ActivityLog.query.filter_by(worker_id=worker.id).order_by(ActivityLog.date.desc()).limit(10).all()
    
    return render_template(
        'worker_medical_records.html.j2',
        worker=worker,
        checkups=checkups,
        vaccinations=vaccinations,
        medical_visits=medical_visits,
        activity_logs=activity_logs
    )

@app.route("/generate-report")
@login_required
def generate_report():
    worker = current_user.worker
    if not worker:
        flash("You must create a worker profile before generating a report.", "warning")
        return redirect(url_for('worker_details'))

    
    # calling Ollama Llama3
    report_content = generate_health_report(worker)
    report_content = report_content.replace("**","")
    
    if "Error:" in report_content:
        flash(report_content, "error")
        return redirect(url_for('dashboard'))


    worker_name = f"{worker.first_name} {worker.last_name or ''}".strip()
    pdf_stream = create_report_pdf(report_content, worker_name)
    
    # 3. Send file to user 
    return send_file(
        pdf_stream,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Health_Report_{worker_name.replace(" ", "_")}.pdf'
    )
# Main Execution 

@app.route("/add-medical-checkup", methods=["GET", "POST"])
@login_required
def add_medical_checkup():
    worker = current_user.worker
    if not worker:
        flash("Please create your profile before adding a medical checkup.", "warning")
        return redirect(url_for('worker_details'))

    checkup_form = MedicalCheckupForm()
    lab_form = LabResultsForm()
    eval_form = DoctorEvaluationForm()

    # Prefill on GET from the latest checkup
    if request.method == 'GET':
        latest = MedicalCheckup.query.filter_by(worker_id=worker.id).order_by(MedicalCheckup.date_of_checkup.desc()).first()
        if latest:
            # MedicalCheckup
            if latest.date_of_checkup:
                checkup_form.date_of_checkup.data = latest.date_of_checkup
            checkup_form.height_cm.data = latest.height_cm
            checkup_form.weight_kg.data = latest.weight_kg
            checkup_form.bmi.data = latest.bmi
            checkup_form.blood_pressure_systolic.data = latest.blood_pressure_systolic
            checkup_form.blood_pressure_diastolic.data = latest.blood_pressure_diastolic
            checkup_form.pulse_rate.data = latest.pulse_rate
            checkup_form.temperature_celsius.data = latest.temperature_celsius
            checkup_form.vision_left.data = latest.vision_left
            checkup_form.vision_right.data = latest.vision_right
            checkup_form.hearing_test_result.data = latest.hearing_test_result.value if latest.hearing_test_result else None
            checkup_form.respiratory_rate.data = latest.respiratory_rate
            checkup_form.oxygen_saturation.data = latest.oxygen_saturation
            checkup_form.checkup_type.data = latest.checkup_type.value if latest.checkup_type else None
            checkup_form.geo_location.data = latest.geo_location

            # LabResults
            if latest.lab_results:
                lab = latest.lab_results
                lab_form.hemoglobin_g_dl.data = lab.hemoglobin_g_dl
                lab_form.blood_sugar_fasting.data = lab.blood_sugar_fasting
                lab_form.blood_sugar_postprandial.data = lab.blood_sugar_postprandial
                lab_form.cholesterol_total.data = lab.cholesterol_total
                lab_form.triglycerides.data = lab.triglycerides
                lab_form.hdl_cholesterol.data = lab.hdl_cholesterol
                lab_form.ldl_cholesterol.data = lab.ldl_cholesterol
                lab_form.hiv_test_result.data = lab.hiv_test_result.value if lab.hiv_test_result else None
                lab_form.hepatitis_b_result.data = lab.hepatitis_b_result.value if lab.hepatitis_b_result else None
                lab_form.hepatitis_c_result.data = lab.hepatitis_c_result.value if lab.hepatitis_c_result else None
                lab_form.tuberculosis_screening_result.data = lab.tuberculosis_screening_result.value if lab.tuberculosis_screening_result else None
                lab_form.malaria_test_result.data = lab.malaria_test_result.value if lab.malaria_test_result else None
                lab_form.urine_test_result.data = lab.urine_test_result.value if lab.urine_test_result else None
                lab_form.xray_chest_result.data = lab.xray_chest_result.value if lab.xray_chest_result else None
                lab_form.ecg_result.data = lab.ecg_result.value if lab.ecg_result else None

            # DoctorEvaluation
            if latest.doctor_evaluation:
                ev = latest.doctor_evaluation
                eval_form.doctor_name.data = ev.doctor_name
                eval_form.doctor_registration_number.data = ev.doctor_registration_number
                eval_form.general_physical_findings.data = ev.general_physical_findings
                eval_form.diagnosis.data = ev.diagnosis
                eval_form.recommendations.data = ev.recommendations
                eval_form.fitness_status.data = ev.fitness_status.value if ev.fitness_status else None
                eval_form.follow_up_required.data = ev.follow_up_required
                eval_form.follow_up_date.data = ev.follow_up_date
                eval_form.signature_of_doctor.data = ev.signature_of_doctor
                eval_form.report_generated_by.data = ev.report_generated_by
                eval_form.report_verified_by.data = ev.report_verified_by
                eval_form.remarks.data = ev.remarks

    # Handle POST for all three forms together
    if checkup_form.validate_on_submit() and lab_form.validate_on_submit() and eval_form.validate_on_submit():
        checkup = MedicalCheckup(
            worker_id=worker.id,
            date_of_checkup=checkup_form.date_of_checkup.data,
            height_cm=checkup_form.height_cm.data,
            weight_kg=checkup_form.weight_kg.data,
            bmi=checkup_form.bmi.data,
            blood_pressure_systolic=checkup_form.blood_pressure_systolic.data,
            blood_pressure_diastolic=checkup_form.blood_pressure_diastolic.data,
            pulse_rate=checkup_form.pulse_rate.data,
            temperature_celsius=checkup_form.temperature_celsius.data,
            vision_left=checkup_form.vision_left.data,
            vision_right=checkup_form.vision_right.data,
            hearing_test_result=checkup_form.hearing_test_result.data,
            respiratory_rate=checkup_form.respiratory_rate.data,
            oxygen_saturation=checkup_form.oxygen_saturation.data,
            checkup_type=checkup_form.checkup_type.data,
            geo_location=checkup_form.geo_location.data
        )

        # Convert enum string values back to enums where necessary
        # from models import HearingResultEnum, CheckupTypeEnum, FitnessStatusEnum, PositiveNegativeEnum, NormalAbnormalEnum
        checkup.hearing_test_result = HearingResultEnum(checkup.hearing_test_result) if checkup.hearing_test_result else None
        checkup.checkup_type = CheckupTypeEnum(checkup.checkup_type) if checkup.checkup_type else None

        db.session.add(checkup)
        db.session.flush()

        lab = LabResults(
            checkup_id=checkup.id,
            hemoglobin_g_dl=lab_form.hemoglobin_g_dl.data,
            blood_sugar_fasting=lab_form.blood_sugar_fasting.data,
            blood_sugar_postprandial=lab_form.blood_sugar_postprandial.data,
            cholesterol_total=lab_form.cholesterol_total.data,
            triglycerides=lab_form.triglycerides.data,
            hdl_cholesterol=lab_form.hdl_cholesterol.data,
            ldl_cholesterol=lab_form.ldl_cholesterol.data,
            hiv_test_result=lab_form.hiv_test_result.data,
            hepatitis_b_result=lab_form.hepatitis_b_result.data,
            hepatitis_c_result=lab_form.hepatitis_c_result.data,
            tuberculosis_screening_result=lab_form.tuberculosis_screening_result.data,
            malaria_test_result=lab_form.malaria_test_result.data,
            urine_test_result=lab_form.urine_test_result.data,
            xray_chest_result=lab_form.xray_chest_result.data,
            ecg_result=lab_form.ecg_result.data
        )
        lab.hiv_test_result = PositiveNegativeEnum(lab.hiv_test_result) if lab.hiv_test_result else None
        lab.hepatitis_b_result = PositiveNegativeEnum(lab.hepatitis_b_result) if lab.hepatitis_b_result else None
        lab.hepatitis_c_result = PositiveNegativeEnum(lab.hepatitis_c_result) if lab.hepatitis_c_result else None
        lab.tuberculosis_screening_result = PositiveNegativeEnum(lab.tuberculosis_screening_result) if lab.tuberculosis_screening_result else None
        lab.malaria_test_result = PositiveNegativeEnum(lab.malaria_test_result) if lab.malaria_test_result else None
        lab.urine_test_result = NormalAbnormalEnum(lab.urine_test_result) if lab.urine_test_result else None
        lab.xray_chest_result = NormalAbnormalEnum(lab.xray_chest_result) if lab.xray_chest_result else None
        lab.ecg_result = NormalAbnormalEnum(lab.ecg_result) if lab.ecg_result else None

        db.session.add(lab)

        ev = DoctorEvaluation(
            checkup_id=checkup.id,
            doctor_name=eval_form.doctor_name.data,
            doctor_registration_number=eval_form.doctor_registration_number.data,
            general_physical_findings=eval_form.general_physical_findings.data,
            diagnosis=eval_form.diagnosis.data,
            recommendations=eval_form.recommendations.data,
            fitness_status=eval_form.fitness_status.data,
            follow_up_required=eval_form.follow_up_required.data,
            follow_up_date=eval_form.follow_up_date.data,
            signature_of_doctor=eval_form.signature_of_doctor.data,
            report_generated_by=eval_form.report_generated_by.data,
            report_verified_by=eval_form.report_verified_by.data,
            remarks=eval_form.remarks.data
        )
        ev.fitness_status = FitnessStatusEnum(ev.fitness_status) if ev.fitness_status else None

        db.session.add(ev)
        db.session.commit()
        flash("Medical checkup saved successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('medical_checkup.html.j2', checkup_form=checkup_form, lab_form=lab_form, eval_form=eval_form, page_title="Add Medical Checkup")


# --- NEW ROUTE FOR FACILITY TO ADD CHECKUP FOR A WORKER ---
@app.route("/worker/<int:worker_id>/add-checkup", methods=["GET", "POST"])
@require_role(["HEALTH_OFFICIAL", "ADMIN"])
def add_checkup_for_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    
    checkup_form = MedicalCheckupForm()
    lab_form = LabResultsForm()
    eval_form = DoctorEvaluationForm()
    
    # Check if all forms are submitted and valid
    if checkup_form.validate_on_submit() and lab_form.validate_on_submit() and eval_form.validate_on_submit():
        # --- This logic is copied from /add-medical-checkup ---
        checkup = MedicalCheckup(
            # --- The ONLY major change is here: ---
            worker_id=worker.id, 
            # ---
            date_of_checkup=checkup_form.date_of_checkup.data,
            height_cm=checkup_form.height_cm.data,
            weight_kg=checkup_form.weight_kg.data,
            bmi=checkup_form.bmi.data,
            blood_pressure_systolic=checkup_form.blood_pressure_systolic.data,
            blood_pressure_diastolic=checkup_form.blood_pressure_diastolic.data,
            pulse_rate=checkup_form.pulse_rate.data,
            temperature_celsius=checkup_form.temperature_celsius.data,
            vision_left=checkup_form.vision_left.data,
            vision_right=checkup_form.vision_right.data,
            hearing_test_result=checkup_form.hearing_test_result.data,
            respiratory_rate=checkup_form.respiratory_rate.data,
            oxygen_saturation=checkup_form.oxygen_saturation.data,
            checkup_type=checkup_form.checkup_type.data,
            geo_location=checkup_form.geo_location.data
        )

        checkup.hearing_test_result = HearingResultEnum(checkup.hearing_test_result) if checkup.hearing_test_result else None
        checkup.checkup_type = CheckupTypeEnum(checkup.checkup_type) if checkup.checkup_type else None

        db.session.add(checkup)
        db.session.flush()

        lab = LabResults(
            checkup_id=checkup.id,
            hemoglobin_g_dl=lab_form.hemoglobin_g_dl.data,
            blood_sugar_fasting=lab_form.blood_sugar_fasting.data,
            blood_sugar_postprandial=lab_form.blood_sugar_postprandial.data,
            cholesterol_total=lab_form.cholesterol_total.data,
            triglycerides=lab_form.triglycerides.data,
            hdl_cholesterol=lab_form.hdl_cholesterol.data,
            ldl_cholesterol=lab_form.ldl_cholesterol.data,
            hiv_test_result=lab_form.hiv_test_result.data,
            hepatitis_b_result=lab_form.hepatitis_b_result.data,
            hepatitis_c_result=lab_form.hepatitis_c_result.data,
            tuberculosis_screening_result=lab_form.tuberculosis_screening_result.data,
            malaria_test_result=lab_form.malaria_test_result.data,
            urine_test_result=lab_form.urine_test_result.data,
            xray_chest_result=lab_form.xray_chest_result.data,
            ecg_result=lab_form.ecg_result.data
        )
        lab.hiv_test_result = PositiveNegativeEnum(lab.hiv_test_result) if lab.hiv_test_result else None
        lab.hepatitis_b_result = PositiveNegativeEnum(lab.hepatitis_b_result) if lab.hepatitis_b_result else None
        lab.hepatitis_c_result = PositiveNegativeEnum(lab.hepatitis_c_result) if lab.hepatitis_c_result else None
        lab.tuberculosis_screening_result = PositiveNegativeEnum(lab.tuberculosis_screening_result) if lab.tuberculosis_screening_result else None
        lab.malaria_test_result = PositiveNegativeEnum(lab.malaria_test_result) if lab.malaria_test_result else None
        lab.urine_test_result = NormalAbnormalEnum(lab.urine_test_result) if lab.urine_test_result else None
        lab.xray_chest_result = NormalAbnormalEnum(lab.xray_chest_result) if lab.xray_chest_result else None
        lab.ecg_result = NormalAbnormalEnum(lab.ecg_result) if lab.ecg_result else None
        db.session.add(lab)

        ev = DoctorEvaluation(
            checkup_id=checkup.id,
            doctor_name=eval_form.doctor_name.data,
            doctor_registration_number=eval_form.doctor_registration_number.data,
            general_physical_findings=eval_form.general_physical_findings.data,
            diagnosis=eval_form.diagnosis.data,
            recommendations=eval_form.recommendations.data,
            fitness_status=eval_form.fitness_status.data,
            follow_up_required=eval_form.follow_up_required.data,
            follow_up_date=eval_form.follow_up_date.data,
            signature_of_doctor=eval_form.signature_of_doctor.data,
            report_generated_by=eval_form.report_generated_by.data,
            report_verified_by=eval_form.report_verified_by.data,
            remarks=eval_form.remarks.data
        )
        ev.fitness_status = FitnessStatusEnum(ev.fitness_status) if ev.fitness_status else None
        db.session.add(ev)
        
        db.session.commit()
        # --- End of copied logic ---
        
        flash(f"Medical checkup for {worker.first_name} saved successfully!", "success")
        return redirect(url_for('view_worker_medical_records', worker_id=worker.id))

    # Prefill on GET from the *specific worker's* latest checkup
    if request.method == 'GET':
        latest = MedicalCheckup.query.filter_by(worker_id=worker.id).order_by(MedicalCheckup.date_of_checkup.desc()).first()
        if latest:
            # You can copy/paste the pre-filling logic from /add-medical-checkup
            # For brevity, I'll just pre-fill one field as an example:
            checkup_form.height_cm.data = latest.height_cm
            # ... (add other pre-fill fields here just like in /add-medical-checkup) ...
            
    # Use the *existing* template!
    return render_template('medical_checkup.html.j2', 
                           checkup_form=checkup_form, 
                           lab_form=lab_form, 
                           eval_form=eval_form,
                           page_title=f"New Checkup for {worker.first_name}")
# --- END OF NEW ROUTE ---


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)