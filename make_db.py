import pymysql
from flask import Flask
from app import app
import os
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("USER")
db_pass = os.getenv("PASS")
db_host = os.getenv("HOST")
db_name = os.getenv("NAME")

# Create Flask app instance
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"


def create_database():
    conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_pass
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"✅ DATABASE {db_name} Checked/Created.")
    cursor.close()
    conn.close()

def create_tables():
    conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100)
        )
    """)

    # Workers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            worker_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            age INT NOT NULL,
            gender VARCHAR(20) NOT NULL,
            phone VARCHAR(100) NOT NULL
        )
    """)

    # Work details table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_details (
            work_id INT AUTO_INCREMENT PRIMARY KEY,
            worker_id INT NOT NULL,
            type_of_work VARCHAR(100) NOT NULL,
            working_hours_per_day INT NOT NULL,
            clean_water_access BOOLEAN,
            FOREIGN KEY (worker_id) REFERENCES workers(worker_id)
        )
    """)

    # Health records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            record_id INT AUTO_INCREMENT PRIMARY KEY,
            worker_id INT NOT NULL,
            height_cm INT NOT NULL,
            weight_kg INT NOT NULL,
            FOREIGN KEY (worker_id) REFERENCES workers(worker_id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tables created/checked.")

if __name__ == "__main__":
    create_database()
    create_tables()
    print("✅ Database and tables are ready!")
