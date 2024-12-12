from flask import Blueprint, render_template, request, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Profile, blocked_users
from sqlalchemy import or_
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def intro():
    return render_template('intro.html', title='intro')

@main_bp.route('/home', methods=['GET'])
@login_required
def home():
    query = request.args.get('query', '').strip()

    preference = current_user.matching_preference
    preferred_genders = preference.preferred_genders.split(',') if preference else []

    blocked_user_ids = [
        row.blocked_id for row in db.session.execute(
            blocked_users.select().where(blocked_users.c.blocker_id == current_user.id)
        ).fetchall()
    ]
    blocked_by_user_ids = [
        row.blocker_id for row in db.session.execute(
            blocked_users.select().where(blocked_users.c.blocked_id == current_user.id)
        ).fetchall()
    ]
    excluded_user_ids = set(blocked_user_ids + blocked_by_user_ids)

    profiles_query = Profile.query.filter(
        Profile.user_id.notin_(excluded_user_ids),
        Profile.user_id != current_user.id
    )

    if preferred_genders:
        profiles_query = profiles_query.filter(Profile.gender.in_(preferred_genders))

    if preference:
        current_year = datetime.utcnow().year
        min_birth_year = current_year - preference.max_age
        max_birth_year = current_year - preference.min_age
        profiles_query = profiles_query.filter(Profile.birth_year.between(min_birth_year, max_birth_year))

    if query:
        profiles_query = profiles_query.filter(Profile.first_name.ilike(f"%{query}%"))

    recommendations = profiles_query.all()

    recommendation_data = []
    for profile in recommendations:
        if profile.photo and profile.photo.file_extension:
            image_url = url_for('static', filename=f"photos/photo-{profile.user_id}.{profile.photo.file_extension}")
        else:
            image_url = url_for('static', filename="images/profile_icon.png")
        recommendation_data.append({
            "id": profile.user_id,
            "name": profile.first_name,
            "image_url": image_url
        })

    return render_template(
        'home.html',
        page_title="Welcome to Dine & Date",
        app_name="Dine & Date",
        query=query,
        recommendations=recommendation_data
    )