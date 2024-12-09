from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, Profile, DateProposal, blocked_users  # blocked_users import
from sqlalchemy import or_
bp = Blueprint('profiles', __name__, url_prefix='/profiles')

# 특정 사용자 프로필 조회 및 렌더링
@bp.route('/view/<int:user_id>', methods=['GET'])
@login_required
def view_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    return render_template(
        'profiles/profile_view.html',
        profile=profile
    )

# 프로필 생성 및 수정
@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        # 사용자 입력값 가져오기
        first_name = request.form.get('first_name')
        gender = request.form.get('gender')
        birth_year = request.form.get('birth_year')
        description = request.form.get('description', None)
        photo_path = request.form.get('photo_path', None)

        # 입력값 검증
        if not first_name or not gender or not birth_year:
            flash("First name, gender, and birth year are required.", "danger")
            return redirect(url_for('profiles.edit_profile'))

        # 프로필 생성 또는 업데이트
        if not profile:
            profile = Profile(
                user_id=current_user.id,
                first_name=first_name,
                gender=gender,
                birth_year=birth_year,
                description=description,
                photo_path=photo_path
            )
            db.session.add(profile)
        else:
            profile.first_name = first_name
            profile.gender = gender
            profile.birth_year = birth_year
            profile.description = description
            profile.photo_path = photo_path

        try:
            db.session.commit()
            flash("Profile updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {e}", "danger")

        return redirect(url_for('profiles.view_profile', user_id=current_user.id))

    return render_template('profiles/profile_edit.html', profile=profile)

@bp.route('/browse', methods=['GET'])
@login_required
def browse_profiles():
    from sqlalchemy import or_

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

    try:
        # 제외된 사용자를 제외하고 프로필 가져오기
        profiles = Profile.query.filter(
            Profile.user_id.notin_(excluded_user_ids),
            Profile.user_id != current_user.id  # 현재 사용자 제외
        ).all()

        if not profiles:
            flash("No profiles available to browse.", "warning")
            return redirect(url_for('home.home'))

        return render_template('profiles/browse_profiles.html', profiles=profiles)
    except Exception as e:
        flash(f"Error browsing profiles: {e}", "danger")
        return redirect(url_for('home.home'))