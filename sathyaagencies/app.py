from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from db import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets

from config import Config


# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = app.config.get(
    "SECRET_KEY",
    "sathya-agencies-development-key"
)

mysql = MySQL(app)


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# ADMIN REQUIRED
# ============================================================

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login as administrator.", "warning")
            return redirect(url_for("admin_login"))

        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("home"))

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT id,
                   gas_name,
                   description,
                   cylinder_size,
                   available_quantity,
                   status
            FROM gases
            WHERE status = 'Available'
            ORDER BY id
        """)

        gases = cursor.fetchall()
        cursor.close()

    except Exception:
        gases = []

    return render_template(
        "home.html",
        gases=gases
    )


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():
    return render_template("about.html")


# ============================================================
# GAS PRODUCTS
# ============================================================

@app.route("/products")
@app.route("/gas-products")
def products():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id,
               gas_name,
               description,
               cylinder_size,
               available_quantity,
               status
        FROM gases
        ORDER BY id
    """)

    gases = cursor.fetchall()
    cursor.close()

    return render_template(
        "products.html",
        gases=gases
    )


# ============================================================
# SERVICES
# ============================================================

@app.route("/services")
def services():
    return render_template("services.html")


# ============================================================
# CONTACT
# ============================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("contact"))

        try:

            cursor = mysql.connection.cursor()

            cursor.execute("""
                INSERT INTO enquiries
                (name, email, phone, message)
                VALUES (%s, %s, %s, %s)
            """, (
                name,
                email,
                phone,
                message
            ))

            mysql.connection.commit()
            cursor.close()

            flash(
                "Your enquiry has been submitted successfully.",
                "success"
            )

        except Exception as e:

            mysql.connection.rollback()

            flash(
                "Unable to submit enquiry.",
                "danger"
            )

        return redirect(url_for("contact"))

    return render_template("contact.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not email or not phone or not password:

            flash(
                "Please fill all required fields.",
                "danger"
            )

            return redirect(url_for("register"))

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(url_for("register"))

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(url_for("register"))

        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()

            flash(
                "An account with this email already exists.",
                "warning"
            )

            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users
            (
                name,
                email,
                phone,
                password_hash,
                role
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'user'
            )
        """, (
            name,
            email,
            phone,
            password_hash
        ))

        mysql.connection.commit()
        cursor.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# ============================================================
# USER LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Enter email and password.",
                "danger"
            )

            return redirect(url_for("login"))

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                phone,
                password_hash,
                role
            FROM users
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()

        cursor.close()

        if user:

            user_id = user[0]
            name = user[1]
            user_email = user[2]
            phone = user[3]
            password_hash = user[4]
            role = user[5]

            if password_hash and check_password_hash(
                password_hash,
                password
            ):

                session.clear()

                session["user_id"] = user_id
                session["user_name"] = name
                session["name"] = name
                session["email"] = user_email
                session["phone"] = phone
                session["role"] = role

                if role == "admin":

                    return redirect(
                        url_for("admin_dashboard")
                    )

                return redirect(
                    url_for("user_dashboard")
                )

        flash(
            "Invalid email or password.",
            "danger"
        )

        return redirect(url_for("login"))

    return render_template("login.html")


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Enter admin email and password.",
                "danger"
            )

            return redirect(url_for("admin_login"))

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                phone,
                password_hash,
                role
            FROM users
            WHERE email = %s
            AND role = 'admin'
        """, (email,))

        admin = cursor.fetchone()

        cursor.close()

        if admin:

            admin_id = admin[0]
            admin_name = admin[1]
            admin_email = admin[2]
            admin_phone = admin[3]
            password_hash = admin[4]

            if password_hash and check_password_hash(
                password_hash,
                password
            ):

                session.clear()

                session["user_id"] = admin_id
                session["user_name"] = admin_name
                session["name"] = admin_name
                session["email"] = admin_email
                session["phone"] = admin_phone
                session["role"] = "admin"

                flash(
                    "Welcome to Admin Dashboard.",
                    "success"
                )

                return redirect(
                    url_for("admin_dashboard")
                )

        flash(
            "Invalid admin email or password.",
            "danger"
        )

        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("home"))


# ============================================================
# USER DASHBOARD
# ============================================================

@app.route("/user/dashboard")
@login_required
def user_dashboard():

    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE user_id = %s
    """, (session["user_id"],))

    total_bookings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE user_id = %s
        AND booking_status = 'Pending'
    """, (session["user_id"],))

    pending_bookings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE user_id = %s
        AND booking_status = 'Delivered'
    """, (session["user_id"],))

    delivered_bookings = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "user_dashboard.html",
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        delivered_bookings=delivered_bookings
    )


# ============================================================
# BOOK CYLINDER
# ============================================================

@app.route("/book", methods=["GET", "POST"])
@login_required
def book_cylinder():

    if session.get("role") == "admin":
        flash(
            "Admin cannot place user bookings.",
            "warning"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            gas_name,
            description,
            cylinder_size,
            available_quantity,
            status
        FROM gases
        WHERE status = 'Available'
        ORDER BY gas_name
    """)

    gases = cursor.fetchall()

    if request.method == "POST":

        gas_id = request.form.get("gas_id")
        quantity = request.form.get("quantity")

        customer_name = request.form.get(
            "customer_name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        pincode = request.form.get(
            "pincode",
            ""
        ).strip()

        try:
            quantity = int(quantity)

        except (ValueError, TypeError):

            cursor.close()

            flash(
                "Invalid quantity.",
                "danger"
            )

            return redirect(
                url_for("book_cylinder")
            )

        if quantity <= 0:

            cursor.close()

            flash(
                "Quantity must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for("book_cylinder")
            )

        cursor.execute("""
            SELECT
                id,
                gas_name,
                cylinder_size,
                available_quantity,
                status
            FROM gases
            WHERE id = %s
        """, (gas_id,))

        gas = cursor.fetchone()

        if not gas:

            cursor.close()

            flash(
                "Selected gas does not exist.",
                "danger"
            )

            return redirect(
                url_for("book_cylinder")
            )

        gas_database_id = gas[0]
        gas_name = gas[1]
        cylinder_size = gas[2]
        available_quantity = gas[3]
        gas_status = gas[4]

        if gas_status != "Available":

            cursor.close()

            flash(
                "This gas is currently unavailable.",
                "danger"
            )

            return redirect(
                url_for("book_cylinder")
            )

        if cylinder_size != "10L":

            cursor.close()

            flash(
                "Only 10L cylinders are available.",
                "danger"
            )

            return redirect(
                url_for("book_cylinder")
            )

        if quantity > available_quantity:

            cursor.close()

            flash(
                f"Only {available_quantity} cylinders are available.",
                "warning"
            )

            return redirect(
                url_for("book_cylinder")
            )

        if (
            not customer_name
            or not phone
            or not email
            or not address
            or not city
            or not pincode
        ):

            cursor.close()

            flash(
                "Please complete all delivery details.",
                "danger"
            )

            return redirect(
                url_for("book_cylinder")
            )

        # Generate unique booking ID
        booking_id = (
            "SA-"
            + secrets.token_hex(4).upper()
        )

        # COD only
        payment_method = "Cash on Delivery"

        cursor.execute("""
            INSERT INTO bookings
            (
                booking_id,
                user_id,
                gas_id,
                quantity,
                cylinder_size,
                customer_name,
                phone,
                email,
                address,
                city,
                pincode,
                payment_method,
                booking_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Pending'
            )
        """, (
            booking_id,
            session["user_id"],
            gas_database_id,
            quantity,
            "10L",
            customer_name,
            phone,
            email,
            address,
            city,
            pincode,
            payment_method
        ))

        cursor.execute("""
            UPDATE gases
            SET available_quantity = available_quantity - %s
            WHERE id = %s
        """, (quantity, gas_database_id))

        mysql.connection.commit()
        cursor.close()

        return render_template(
            "booking_confirmation.html",
            booking_id=booking_id,
            gas_name=gas_name,
            quantity=quantity,
            cylinder_size="10L",
            customer_name=customer_name,
            phone=phone,
            email=email,
            address=address,
            city=city,
            pincode=pincode,
            payment_method=payment_method
        )

    cursor.close()

    return render_template(
        "book.html",
        gases=gases
    )


# ============================================================
# MY BOOKINGS
# ============================================================

@app.route("/my-bookings")
@login_required
def my_bookings():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            b.booking_id,
            g.gas_name,
            b.quantity,
            b.cylinder_size,
            b.payment_method,
            b.booking_status,
            b.created_at
        FROM bookings b
        INNER JOIN gases g
            ON b.gas_id = g.id
        WHERE b.user_id = %s
        ORDER BY b.created_at DESC
    """, (session["user_id"],))

    bookings = cursor.fetchall()

    cursor.close()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )


# ============================================================
# BOOKING DETAILS
# ============================================================

@app.route("/booking/<booking_id>")
@login_required
def booking_details(booking_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            b.booking_id,
            g.gas_name,
            b.quantity,
            b.cylinder_size,
            b.customer_name,
            b.phone,
            b.email,
            b.address,
            b.city,
            b.pincode,
            b.payment_method,
            b.booking_status,
            b.created_at,
            b.updated_at
        FROM bookings b
        INNER JOIN gases g
            ON b.gas_id = g.id
        WHERE b.booking_id = %s
        AND b.user_id = %s
    """, (
        booking_id,
        session["user_id"]
    ))

    booking = cursor.fetchone()

    cursor.close()

    if not booking:

        flash(
            "Booking not found.",
            "danger"
        )

        return redirect(
            url_for("my_bookings")
        )

    return render_template(
        "booking_details.html",
        booking=booking
    )


# ============================================================
# CANCEL BOOKING
# ============================================================

@app.route("/booking/<booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            gas_id,
            quantity,
            booking_status
        FROM bookings
        WHERE booking_id = %s
        AND user_id = %s
    """, (
        booking_id,
        session["user_id"]
    ))

    booking = cursor.fetchone()

    if not booking:

        cursor.close()

        flash(
            "Booking not found.",
            "danger"
        )

        return redirect(
            url_for("my_bookings")
        )

    booking_db_id = booking[0]
    gas_id = booking[1]
    quantity = booking[2]
    status = booking[3]

    if status != "Pending":

        cursor.close()

        flash(
            "This booking can no longer be cancelled.",
            "warning"
        )

        return redirect(
            url_for("my_bookings")
        )

    cursor.execute("""
        UPDATE bookings
        SET booking_status = 'Cancelled',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (booking_db_id,))

    # Restore inventory
    cursor.execute("""
        UPDATE gases
        SET available_quantity =
            available_quantity + %s
        WHERE id = %s
    """, (
        quantity,
        gas_id
    ))

    mysql.connection.commit()
    cursor.close()

    flash(
        "Booking cancelled successfully.",
        "success"
    )

    return redirect(
        url_for("my_bookings")
    )


# ============================================================
# USER PROFILE
# ============================================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        pincode = request.form.get(
            "pincode",
            ""
        ).strip()

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE users
            SET
                name = %s,
                phone = %s,
                address = %s,
                city = %s,
                pincode = %s
            WHERE id = %s
        """, (
            name,
            phone,
            address,
            city,
            pincode,
            session["user_id"]
        ))

        mysql.connection.commit()
        cursor.close()

        session["user_name"] = name
        session["name"] = name
        session["phone"] = phone

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("profile")
        )

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            address,
            city,
            pincode,
            role
        FROM users
        WHERE id = %s
    """, (session["user_id"],))

    user = cursor.fetchone()

    cursor.close()

    return render_template(
        "profile.html",
        user=user
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    cursor = mysql.connection.cursor()

    # Users
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role = 'user'
    """)

    total_users = cursor.fetchone()[0]

    # Bookings
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
    """)

    total_bookings = cursor.fetchone()[0]

    # Pending
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE booking_status = 'Pending'
    """)

    pending_bookings = cursor.fetchone()[0]

    # Confirmed
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE booking_status = 'Confirmed'
    """)

    confirmed_bookings = cursor.fetchone()[0]

    # Delivered
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE booking_status = 'Delivered'
    """)

    delivered_bookings = cursor.fetchone()[0]

    # Cancelled
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE booking_status = 'Cancelled'
    """)

    cancelled_bookings = cursor.fetchone()[0]

    # Gas inventory
    cursor.execute("""
        SELECT
            id,
            gas_name,
            description,
            cylinder_size,
            available_quantity,
            status
        FROM gases
        ORDER BY id
    """)

    gases = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        confirmed_bookings=confirmed_bookings,
        delivered_bookings=delivered_bookings,
        cancelled_bookings=cancelled_bookings,
        gases=gases
    )


# ============================================================
# ADMIN - MANAGE PRODUCTS
# ============================================================

@app.route("/admin/products")
@admin_required
def admin_products():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            gas_name,
            description,
            cylinder_size,
            available_quantity,
            status
        FROM gases
        ORDER BY id
    """)

    gases = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_products.html",
        gases=gases
    )


# ============================================================
# ADMIN - UPDATE INVENTORY
# ============================================================

@app.route("/admin/inventory/update/<int:gas_id>", methods=["POST"])
@admin_required
def update_inventory(gas_id):

    quantity = request.form.get(
        "available_quantity",
        "0"
    )

    status = request.form.get(
        "status",
        "Available"
    )

    try:
        quantity = int(quantity)

        if quantity < 0:
            raise ValueError

    except ValueError:

        flash(
            "Invalid inventory quantity.",
            "danger"
        )

        return redirect(
            url_for("admin_products")
        )

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE gases
        SET
            available_quantity = %s,
            status = %s
        WHERE id = %s
    """, (
        quantity,
        status,
        gas_id
    ))

    mysql.connection.commit()
    cursor.close()

    flash(
        "Inventory updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin_products")
    )


# ============================================================
# ADMIN - BOOKINGS
# ============================================================

@app.route("/admin/bookings")
@admin_required
def admin_bookings():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            b.id,
            b.booking_id,
            b.customer_name,
            b.phone,
            b.email,
            g.gas_name,
            b.quantity,
            b.cylinder_size,
            b.address,
            b.city,
            b.pincode,
            b.payment_method,
            b.booking_status,
            b.created_at
        FROM bookings b
        INNER JOIN gases g
            ON b.gas_id = g.id
        ORDER BY b.created_at DESC
    """)

    bookings = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_bookings.html",
        bookings=bookings
    )


# ============================================================
# ADMIN - CHANGE BOOKING STATUS
# ============================================================

@app.route(
    "/admin/bookings/<int:booking_db_id>/status",
    methods=["POST"]
)
@admin_required
def update_booking_status(booking_db_id):

    new_status = request.form.get(
        "booking_status"
    )

    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    ]

    if new_status not in allowed_statuses:

        flash(
            "Invalid booking status.",
            "danger"
        )

        return redirect(
            url_for("admin_bookings")
        )

    cursor = mysql.connection.cursor()

    # Get current booking
    cursor.execute("""
        SELECT
            gas_id,
            quantity,
            booking_status
        FROM bookings
        WHERE id = %s
    """, (booking_db_id,))

    booking = cursor.fetchone()

    if not booking:

        cursor.close()

        flash(
            "Booking not found.",
            "danger"
        )

        return redirect(
            url_for("admin_bookings")
        )

    gas_id = booking[0]
    quantity = booking[1]
    old_status = booking[2]

    # Cancel only once
    if (
        new_status == "Cancelled"
        and old_status != "Cancelled"
    ):

        cursor.execute("""
            UPDATE gases
            SET available_quantity =
                available_quantity + %s
            WHERE id = %s
        """, (
            quantity,
            gas_id
        ))

    cursor.execute("""
        UPDATE bookings
        SET
            booking_status = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (
        new_status,
        booking_db_id
    ))

    mysql.connection.commit()
    cursor.close()

    flash(
        "Booking status updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin_bookings")
    )


# ============================================================
# ADMIN - USERS
# ============================================================

@app.route("/admin/users")
@admin_required
def admin_users():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            role,
            city,
            created_at
        FROM users
        ORDER BY created_at DESC
    """)

    users = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_users.html",
        users=users
    )


# ============================================================
# ADMIN - ENQUIRIES
# ============================================================

@app.route("/admin/enquiries")
@admin_required
def admin_enquiries():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            message,
            created_at
        FROM enquiries
        ORDER BY created_at DESC
    """)

    enquiries = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_enquiries.html",
        enquiries=enquiries
    )


# ============================================================
# ADMIN PROFILE
# ============================================================

@app.route("/admin/profile")
@admin_required
def admin_profile():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            role
        FROM users
        WHERE id = %s
    """, (session["user_id"],))

    admin = cursor.fetchone()

    cursor.close()

    return render_template(
        "admin_profile.html",
        admin=admin
    )


# ============================================================
# DATABASE TEST
# ============================================================

@app.route("/test")
def test():

    try:

        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT DATABASE()"
        )

        database = cursor.fetchone()

        cursor.close()

        return f"""
        <html>
        <head>
            <title>Sathya Agencies Test</title>
        </head>
        <body>
            <h1>Sathya Agencies</h1>
            <p>Flask Application is Working!</p>
            <p>MySQL Connection is Working!</p>
            <p>Database: {database[0]}</p>
            <p><a href="/login">User Login</a></p>
            <p><a href="/admin/login">Admin Login</a></p>
        </body>
        </html>
        """

    except Exception as e:

        return f"""
        <h1>Database Connection Error</h1>
        <p>{e}</p>
        """


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404 - Page Not Found</h1>
    <p>The requested page does not exist.</p>
    <a href="/">Go Home</a>
    """, 404


@app.errorhandler(500)
def internal_error(error):

    return """
    <h1>500 - Internal Server Error</h1>
    <p>Something went wrong.</p>
    <a href="/">Go Home</a>
    """, 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
