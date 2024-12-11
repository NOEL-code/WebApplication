import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Profile, Photo

bp = Blueprint('auth', __name__, url_prefix='/auth')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_photo_directory():
    """Ensure the photo storage directory exists."""
    directory = os.path.join(current_app.static_folder, "photos")
    if not os.path.exists(directory):
        os.makedirs(directory)

def photo_filename(photo):
    """Construct the file path for the photo."""
    directory = os.path.join(current_app.static_folder, "photos")
    return os.path.join(directory, f"photo-{photo.id}.{photo.file_extension}")

@bp.route('/register', methods=['GET'])
def register_form():
    from datetime import datetime
    current_year = datetime.now().year
    return render_template('auth/register.html', current_year=current_year)

@bp.route('/register_photo', methods=['POST'])
def register_photo():
    print("회원가입 시작")
    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    gender = request.form.get('gender')
    birth_year = request.form.get('birth_year')
    description = request.form.get('description', "Welcome to Dine & Date!")
    photo = request.files.get('photo')

    if not email or not password or not first_name or not gender or not birth_year or not photo:
        print("All fields are required.", "danger")
        return redirect(url_for('auth.register_form'))

    if User.query.filter_by(email=email).first():
        print("Email already exists.", "danger")
        return redirect(url_for('auth.register_form'))

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    default_profile = Profile(
        user_id=new_user.id,
        first_name=first_name,
        gender=gender,
        birth_year=int(birth_year),
        description=description
    )
    db.session.add(default_profile)
    db.session.commit()

    if photo and allowed_file(photo.filename):
        ensure_photo_directory()
        file_extension = photo.filename.rsplit('.', 1)[1].lower()

        # 데이터베이스에 저장
        photo_obj = Photo(file_extension=file_extension, profile_id=default_profile.id)
        db.session.add(photo_obj)
        db.session.commit()

        # 사진 저장 경로 생성
        photo_path = photo_filename(photo_obj)
        try:
            photo.save(photo_path)
            print(f"Photo saved at {photo_path}")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving photo: {e}")
            print("Failed to upload the photo.", "danger")
            return redirect(url_for('auth.register_form'))
    elif photo:
        print("Unsupported file type.", "danger")
        return redirect(url_for('auth.register_form'))

    flash("User registered successfully. Please log in.", "success")
    return redirect(url_for('auth.login_form'))

@bp.route('/login', methods=['GET'])
def login_form():
    return render_template('auth/login.html')

@bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash("Email and password are required.", "danger")
        return redirect(url_for('auth.login_form'))

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        flash("Invalid email or password.", "danger")
        return redirect(url_for('auth.login_form'))

    login_user(user)
    flash("Login successful.", "success")
    return redirect(url_for('main.home'))

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Logout successful.", "success")
    return redirect(url_for('auth.login_form'))

@bp.route('/current-user', methods=['GET'])
@login_required
def current_user_info():
    return jsonify({
        "user_id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }), 200