import os
from flask import Flask
from dotenv import load_dotenv

# Import db and models
from database import db
from models import (
    User, Worker, HealthRecord,
    HealthcareFacility, MedicalVisit, Vaccination
)

# Load environment variables
load_dotenv()

#  App Initialization 
app = Flask(__name__)

#  Database Configuration 
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Bind db to app
db.init_app(app)



@app.route("/")
def home():
    return "Welcome to CuraVie."



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/checked.")

    app.run(debug=True)
