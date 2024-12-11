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

    # 매칭 선호도 조건 추가
    preference = current_user.matching_preference
    preferred_genders = preference.preferred_genders.split(',') if preference else []

    # 차단된 사용자 목록 가져오기
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

    # 추천 프로필 필터링
    profiles_query = Profile.query.filter(
        Profile.user_id.notin_(excluded_user_ids),
        Profile.user_id != current_user.id
    )

    if preferred_genders:
        profiles_query = profiles_query.filter(Profile.gender.in_(preferred_genders))

    if query:
        profiles_query = profiles_query.filter(Profile.first_name.ilike(f"%{query}%"))

    recommendations = profiles_query.all()

    # 사진 경로 포함
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