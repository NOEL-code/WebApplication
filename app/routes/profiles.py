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
    filename = f"photo-{profile_id}.{file_extension}"
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

    # Construct photo path
    photo_path = url_for('static', filename='images/profile_icon.png')  # 기본 이미지
    if profile.photo and profile.photo.file_extension:
        photo_path = url_for('static', filename=f"photos/photo-{profile.id}.{profile.photo.file_extension}")

    return render_template(
        'users/users.html',
        profile=profile,
        photo_path=photo_path  # 이미지 경로 전달
    )


@bp.route('/view_my/<int:user_id>', methods=['GET'])
@login_required
def view_my_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for('main.home'))

    # 프로필 이미지 경로 생성
    photo_path = None
    if profile.photo and profile.photo.file_extension:
        photo_path = url_for('static', filename=f"photos/photo-{profile.id}.{profile.photo.file_extension}")

    return render_template(
        'users/user_profile.html',
        profile=profile,
        photo_path=photo_path  # 이미지 경로 전달
    )

@bp.route('/edit', methods=['POST'])
@login_required
def edit_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    first_name = request.form.get('first_name')
    gender = request.form.get('gender')
    birth_year = request.form.get('birth_year')
    description = request.form.get('description')
    photo = request.files.get('photo')

    if first_name:
        profile.first_name = first_name
    if gender:
        profile.gender = GenderEnum[gender]
    if birth_year:
        profile.birth_year = int(birth_year)
    if description:
        profile.description = description

    if photo and allowed_file(photo.filename):
        file_extension = photo.filename.rsplit('.', 1)[1].lower()
        filename = f"photo-{profile.id}.{file_extension}"
        photo_path = os.path.join(current_app.static_folder, "photos", filename)
        photo.save(photo_path)

        if profile.photo:
            profile.photo.file_extension = file_extension
        else:
            new_photo = Photo(file_extension=file_extension, profile_id=profile.id)
            db.session.add(new_photo)

    try:
        db.session.commit()
        flash("Profile updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating profile: {e}", "danger")

    return redirect(url_for('profiles.view_my_profile', user_id=current_user.id))

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