from flask import Blueprint, request, jsonify
from app.models import db, User, Profile

bp = Blueprint('profiles', __name__, url_prefix='/profiles')

# 프로필 생성 및 수정
@bp.route('/update', methods=['POST', 'PUT'])
def update_profile():
    data = request.json
    user_id = data.get('user_id')
    first_name = data.get('first_name')
    gender = data.get('gender')
    birth_year = data.get('birth_year')
    description = data.get('description', None)
    photo_path = data.get('photo_path', None)

    # 입력값 확인
    if not user_id or not first_name or not gender or not birth_year:
        return jsonify({"error": "user_id, first_name, gender, and birth_year are required"}), 400

    # 사용자 확인
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 프로필 조회
    profile = Profile.query.filter_by(user_id=user_id).first()

    # 프로필 없으면 생성
    if not profile:
        profile = Profile(
            user_id=user_id,
            first_name=first_name,
            gender=gender,
            birth_year=birth_year,
            description=description,
            photo_path=photo_path
        )
        db.session.add(profile)
    else:
        # 기존 프로필 업데이트
        profile.first_name = first_name
        profile.gender = gender
        profile.birth_year = birth_year
        profile.description = description
        profile.photo_path = photo_path

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200

# 특정 사용자 프로필 조회
@bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify({
        "user_id": profile.user_id,
        "first_name": profile.first_name,
        "gender": profile.gender,
        "birth_year": profile.birth_year,
        "description": profile.description,
        "photo_path": profile.photo_path
    }), 200

# 모든 사용자 프로필 조회
@bp.route('/list', methods=['GET'])
def list_profiles():
    profiles = Profile.query.all()
    profile_list = [{
        "user_id": profile.user_id,
        "first_name": profile.first_name,
        "gender": profile.gender,
        "birth_year": profile.birth_year,
        "description": profile.description,
        "photo_path": profile.photo_path
    } for profile in profiles]

    return jsonify(profile_list), 200