from flask import Blueprint, redirect, url_for, session
from functools import wraps

admin = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("admin_login"))
        if session.get("role") != "admin":
            return redirect(url_for("home"))
        return function(*args, **kwargs)
    return wrapper

@admin.route("/login")
def login():
    return redirect(url_for("admin_login"))

@admin.route("/dashboard")
@admin_required
def dashboard():
    return redirect(url_for("admin_dashboard"))

@admin.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
