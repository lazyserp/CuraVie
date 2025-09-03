import os
from flask import Flask, render_template,request,jsonify
from dotenv import load_dotenv
from models import User, UserRoleEnum, Worker, WorkDetail, HealthRecord, HealthcareFacility, MedicalVisit, Vaccination

# Import db from our new database.py file
from database import db

# Load environment variables from .env file
load_dotenv()

# --- App Initialization ---
app = Flask(__name__)

# --- Database Configuration ---
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db object with our app
db.init_app(app)

# Import models AFTER initializing db
from models import Worker, WorkDetail, HealthRecord

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html.j2")

@app.route("/api/admin/register",methods=['POST'])
def register_admin():
    data  = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error":"Username and password are required"}), 400 

    #Check if alrady exists
    if User.query.filter_by(username=data.get('username')).first() or User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Username or email already exists"}), 409

    try:
        #create new admin user
        new_admin = User(
            username = data.get('username'),
            email=data.get('email'),
            role = UserRoleEnum.ADMIN
            )
        new_admin.set_password(data.get('password'))
        db.session.add(new_admin)
        db.session.commit()

        return jsonify({"message": "Admin user created successfully", "user_id": new_admin.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- Main Execution ---
if __name__ == "__main__":
    with app.app_context():
        # This command creates the tables based on your models
        db.create_all()
        print("✅ Database tables created/checked.")
    
    app.run(debug=True)