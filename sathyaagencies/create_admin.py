import os
from werkzeug.security import generate_password_hash
from app import app, mysql

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@sathyaagencies.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@12345")

with app.app_context():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (ADMIN_EMAIL,))
    existing = cursor.fetchone()
    if existing:
        print("Admin account already exists:", ADMIN_EMAIL)
    else:
        cursor.execute("""
            INSERT INTO users (name,email,phone,password_hash,role)
            VALUES (%s,%s,%s,%s,'admin')
        """, ("Sathya Agencies Admin", ADMIN_EMAIL, "6381556231", generate_password_hash(ADMIN_PASSWORD)))
        mysql.connection.commit()
        print("Admin account created:", ADMIN_EMAIL)
    cursor.close()
