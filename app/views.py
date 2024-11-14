from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Profile, DateProposal
from . import db

main = Blueprint("main", __name__)

@main.route("/login")
def login():
    return render_template("auth/login.html")

@main.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    return render_template("profile.html", user=user)

@main.route("/propose_date/<int:recipient_id>")
@login_required
def propose_date(recipient_id):
    recipient = User.query.get(recipient_id)
    # Implement logic for proposing a date
    return render_template("propose_date.html", recipient=recipient)
