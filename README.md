# 🚑 CuraVie: AI-Powered Health Records for Migrant Workers  

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)  
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)  
![MySQL](https://img.shields.io/badge/Database-MySQL-orange?logo=mysql)  
![License](https://img.shields.io/badge/License-MIT-green)  
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)  

---

A **digital health record management system** for **migrant workers in Kerala**, built for the **SIH 2025 Hackathon**.  
This project aims to provide **accessible health tracking** and **AI-powered preventive guidance**.  

---

## 🎨 Design  

<img width="1902" height="912" alt="image" src="https://github.com/user-attachments/assets/3e7de142-50d8-4d36-b4d9-4d6ed44edcc9" />  

<img width="1919" height="914" alt="image" src="https://github.com/user-attachments/assets/a07bd35e-a221-455b-a6b9-e2624cc21f5f" />  

<img width="1917" height="918" alt="image" src="https://github.com/user-attachments/assets/f9ec1ae9-4094-480f-a530-d530bff67bd9" />  

<img width="1903" height="913" alt="image" src="https://github.com/user-attachments/assets/c94c20e9-775c-4600-acac-960a46d569e7" />  

---

## 📊 Sample Report  

<img width="632" height="837" alt="image" src="https://github.com/user-attachments/assets/8b0bc1bb-0952-4272-b4b4-368a62d01d34" />  

---

## 🩺 Problem & Solution  

**Problem:**  
Migrant workers often lack consistent healthcare access and portable medical records.  

**Solution:**  
Our solution is a **centralized digital platform** that collects a worker's **occupational, lifestyle, and health data**.  
An **AI model** generates **personalized health risk reports** and **preventive recommendations**, delivered in the user's **preferred language**.  

---

## ✨ Key Features  

- **User Authentication**: Secure signup, login, and session management.  
- **Detailed Worker Profile**: Captures personal, occupational (e.g., construction, agriculture), and lifestyle data (e.g., diet, smoking, alcohol habits).  
- **Profile Management**: Users can create and edit their profile via the dashboard.  
- **Structured Database**: SQLAlchemy + MySQL schema for users, workers, and health records.  
- **Multilingual UI**: Frontend supports localization via translation keys.  

---

## 🛠 Tech Stack  

- **Backend**: Python, Flask, SQLAlchemy  
- **Database**: MySQL  
- **Frontend**: HTML, CSS, JavaScript  
- **AI/ML**: Ollama  
- **Libraries**: Flask-WTF, Flask-Login, PyMySQL, WeasyPrint  

---

## ⚡ Quick Start  

### 1. Prerequisites  
- Python 3.9+  
- Git  
- Running MySQL server
- GTK for Windows

---

### 2. Setup  

```bash
# Clone the repository
git clone <your-repository-url>
cd <repository-name>

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
3. Configuration

Create a .env file in the root directory with your database details:

DB_USER="your_mysql_user"
DB_PASS="your_mysql_password"
DB_HOST="localhost"
DB_NAME="curavie"
SECRET_KEY="a-strong-random-secret-key"

4. Initialize Database

Create a database in MySQL named curavie:

CREATE DATABASE curavie;

5. Run the Application
flask run


The app will be available at:
👉 http://127.0.0.1:5000
