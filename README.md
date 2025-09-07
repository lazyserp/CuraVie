# CuraVie: AI-Powered Health Records for Migrant Workers
A digital health record management system for migrant workers in Kerala, built for the SIH 2025 Hackathon. This project aims to provide accessible health tracking and AI-powered preventive guidance.

<img width="1919" height="899" alt="image" src="https://github.com/user-attachments/assets/f3e3373c-4e93-4521-b25a-e2f5a4c46560" />
<img width="1917" height="904" alt="image" src="https://github.com/user-attachments/assets/6bbd860e-cde7-46ec-9f02-4ac1986b58ff" />

# Problem & Solution
Migrant workers often lack consistent healthcare access and portable medical records. Our solution is a centralized digital platform that collects a user's occupational, lifestyle, and health data. An AI model will then generate personalized health risk reports and preventive recommendations, delivered in the user's preferred language.

# Key Features

User Authentication: Secure user signup, login, and session management.
Detailed Worker Profile: Collects personal, occupational (e.g., construction, agriculture), and lifestyle data (e.g., diet, smoking/alcohol habits).
Profile Management: Users can create their profile after signing up and can edit it later via the dashboard.
Structured Database: Uses SQLAlchemy and MySQL to create a robust schema for users, workers, health records, and more.
Multilingual UI: Frontend is designed with translation keys for easy localization.

# Tech Stack
Backend: Python, Flask, SQLAlchemy
Database: MySQL
Frontend: HTML, CSS, JavaScript
AI/ML: Ollama, OpenAI API
Libraries: Flask-WTF, Flask-Login, PyMySQL


# Quick Start
1. Prerequisites
Python 3.9+
Git
A running MySQL server

2. Setup
Bash
# Clone the repository
git clone <your-repository-url>
cd <repository-name>

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install Flask Flask-Login Flask-WTF Flask-SQLAlchemy PyMySQL python-dotenv
3. Configuration
Create a .env file in the root directory with your database details:

DB_USER="your_mysql_user"
DB_PASS="your_mysql_password"
DB_HOST="localhost"
DB_NAME="curavie_db"
SECRET_KEY="a-strong-random-secret-key"
4. Initialize Database
Run the setup script to create the database and tables:

Bash

python make_db.py
5. Run the App
Bash

flask run
The application will be available at http://1227.0.0.1:5000.
