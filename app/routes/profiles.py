from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import os
import pathlib
from werkzeug.utils import secure_filename
from app.models import db, Profile, Photo, User, DateProposal, blocked_users, GenderEnum
from sqlalchemy import or_

bp = Blueprint('profiles', __name__, url_prefix='/profiles')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_photo_directory():
    """Ensure the photo storage directory exists."""
    directory = pathlib.Path(current_app.root_path) / "static" / "photos"
    if not directory.exists():
        directory.mkdir(parents=True)
    return directory

def save_photo(photo, profile_id):
    """Save photo file to the server and return its relative path."""
    ensure_photo_directory()
    file_extension = photo.filename.rsplit('.', 1)[1].lower()
    filename = f"profile-{profile_id}.{file_extension}"
    photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    photo.save(photo_path)
    return f"photos/{filename}"

@bp.route('/view/<int:user_id>', methods=['GET'])
@login_required
def view_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for('main.home'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('main.home'))

    return render_template(
        'users/users.html',
        profile=profile,
        user=user
    )

@bp.route('/view_my/<int:user_id>', methods=['GET'])
@login_required
def view_my_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for('main.home'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('main.home'))

    return render_template(
        'users/user_profile.html',
        profile=profile,
        user=user
    )

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
        photo = request.files.get('photo')

        # 입력값 검증
        if not first_name or not gender or not birth_year:
            flash("First name, gender, and birth year are required.", "danger")
            return redirect(url_for('profiles.edit_profile'))
    
        # 프로필 업데이트
        profile.first_name = first_name
        profile.gender = GenderEnum[gender]  # 문자열을 Enum으로 변환
        profile.birth_year = int(birth_year)
        profile.description = description
        
        print(gender)
        print(profile.gender)
        # 사진 업로드 처리
        if photo and allowed_file(photo.filename):
            try:
                relative_photo_path = save_photo(photo, profile.id)
                profile.photo_path = relative_photo_path
            except Exception as e:
                db.session.rollback()
                flash(f"Error saving photo: {e}", "danger")
                return redirect(url_for('profiles.edit_profile'))
        elif photo:
            flash("Unsupported file type.", "danger")
            return redirect(url_for('profiles.edit_profile'))

        # 데이터베이스에 변경사항 저장
        try:
            db.session.commit()
            flash("Profile updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {e}", "danger")

        return redirect(url_for('main.home'))

    return render_template('users/user_profile.html', profile=profile)

@bp.route('/browse', methods=['GET'])
@login_required
def browse_profiles():
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
        profiles = Profile.query.filter(
            Profile.user_id.notin_(excluded_user_ids),
            Profile.user_id != current_user.id  # 현재 사용자 제외
        ).all()

        if not profiles:
            flash("No profiles available to browse.", "warning")
            return redirect(url_for('main.home'))

        return render_template('profiles/browse_profiles.html', profiles=profiles)
    except Exception as e:
        flash(f"Error browsing profiles: {e}", "danger")
        return redirect(url_for('main.home'))