from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 회원가입
@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # 중복 이메일 체크
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    # 비밀번호 해싱 및 사용자 생성
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# 로그인
@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # 사용자 확인
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # 세션에 사용자 ID 저장
    session['user_id'] = user.id
    return jsonify({"message": "Login successful", "user_id": user.id}), 200

# 로그아웃
@bp.route('/logout', methods=['POST'])
def logout():
    # 세션에서 사용자 ID 제거
    session.pop('user_id', None)
    return jsonify({"message": "Logout successful"}), 200

# 현재 로그인된 사용자 정보 확인
@bp.route('/current-user', methods=['GET'])
def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No user is logged in"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }), 200