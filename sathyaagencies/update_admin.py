from werkzeug.security import generate_password_hash
from app import app, mysql

ADMIN_EMAIL = "sathyaagencies61@gmail.com"
ADMIN_PASSWORD = "sathyaagencies61"

print("Starting admin update...")

with app.app_context():

    cursor = mysql.connection.cursor()

    password_hash = generate_password_hash(ADMIN_PASSWORD)

    cursor.execute(
        """
        UPDATE users
        SET
            name = %s,
            password_hash = %s,
            role = 'admin'
        WHERE email = %s
        """,
        (
            "Sathya Agencies",
            password_hash,
            ADMIN_EMAIL
        )
    )

    mysql.connection.commit()

    if cursor.rowcount > 0:
        print("Admin email and password updated successfully.")
        print("Email:", ADMIN_EMAIL)
        print("Password:", ADMIN_PASSWORD)
    else:
        print("No admin account found with this email.")
        print("Email:", ADMIN_EMAIL)

    cursor.close()

print("Update completed.")