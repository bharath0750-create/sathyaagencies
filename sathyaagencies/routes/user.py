from flask import Blueprint, render_template, redirect, url_for, session
from functools import wraps

user = Blueprint("user", __name__, url_prefix="/user")

def user_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "user":
            return redirect(url_for("home"))
        return function(*args, **kwargs)
    return wrapper

@user.route("/dashboard")
@user_required
def dashboard():
    return redirect(url_for("user_dashboard"))
