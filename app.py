import os
from flask import Flask,render_template,redirect,flash,request,url_for
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import User
from forms import SignUpForm
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect


# Import db and models
from database import db
from models import (
    User, Worker, HealthRecord,
    MedicalVisit, Vaccination
)

# Load environment variables
load_dotenv()

#  App Initialization 
app = Flask(__name__)
csrf = CSRFProtect(app)

#  Database Configuration 
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

# Bind db to app
db.init_app(app)


# Initializing LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        
        if User.query.filter_by(username=username).first():
            flash("Username already taken. Choose another.", "danger")
            return render_template("signup.html.j2", form=form)

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Did you forget your password?", "danger")
            return render_template("signup.html.j2", form=form)

        # Create user object and set hashed password
        user = User(username=username, email=email)
        user.set_password(password)

        # Save to DB with error
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("An account with that username or email already exists.", "danger")
            return render_template("signup.html.j2", form=form)

        flash("Account created — please sign in.", "success")
        # Optionally auto-login:
        # from flask_login import login_user
        # login_user(user)
        return redirect(url_for("login"))

    # GET or validation failed -> render form with errors
    return render_template("signup.html.j2", form=form)


@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('login Successful','success')
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password","danger")
        
    return render_template('login.html.j2')

@login_required
@app.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.','info')
    return redirect(url_for('login'))


@login_required
@app.route("/dashboard")
def dashboard():
    return f"Welcome {current_user.username}!"
@app.route("/")
def home():
    return render_template('index.html.j2')



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/checked.")

    app.run(debug=True)

