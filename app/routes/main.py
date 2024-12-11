from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from datetime import datetime  # 수정: Python 표준 라이브러리에서 가져오기
from app.models import db, Profile, DateProposal, blocked_users

# 메인 페이지 블루프린트 생성
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def intro():
    return render_template('intro.html', title='intro')

@main_bp.route('/home')
@login_required
def home():
    # 사용자의 매칭 선호도 가져오기
    preference = current_user.matching_preference

    if not preference:
        flash("Please set your matching preferences.", "warning")
        return redirect(url_for('preferences.edit_preferences'))

    # 현재 사용자가 차단한 사용자 및 차단된 사용자 ID 가져오기
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

    # 차단 관계에 있는 사용자 목록
    excluded_user_ids = set(blocked_user_ids + blocked_by_user_ids)

    # 현재 사용자가 이미 데이트 제안을 주고받은 사용자 ID 가져오기
    proposal_user_ids = [
        proposal.proposer_id if proposal.recipient_id == current_user.id else proposal.recipient_id
        for proposal in DateProposal.query.filter(
            or_(
                DateProposal.proposer_id == current_user.id,
                DateProposal.recipient_id == current_user.id
            )
        ).all()
    ]

    # 최종 제외할 사용자 ID (차단 + 제안 관계)
    excluded_user_ids.update(proposal_user_ids)
    excluded_user_ids = list(excluded_user_ids)  # 리스트로 변환

    # 선호도를 기준으로 추천 사용자 필터링
    preferred_genders = preference.preferred_genders.split(',')  # 선호 성별
    current_year = datetime.utcnow().year
    min_birth_year = current_year - preference.max_age
    max_birth_year = current_year - preference.min_age

    recommendations = Profile.query.filter(
        Profile.user_id.notin_(excluded_user_ids),  # 제외된 사용자 제외
        Profile.user_id != current_user.id,  # 현재 사용자 제외
        Profile.gender.in_(preferred_genders),  # 선호 성별
        Profile.birth_year.between(min_birth_year, max_birth_year)  # 선호 나이대
    ).limit(10).all()  # 최대 10명의 추천 사용자

    return render_template(
        'home.html',
        page_title="Welcome to Dine & Date",
        app_name="Dine & Date",
        recommendations=[
            {
                "id": person.user_id,
                "name": person.first_name,
                "image_url": f"photos/profile-{person.user_id}.jpg" if person.photo else "images/default_profile.png"
            }
            for person in recommendations
        ]
    )