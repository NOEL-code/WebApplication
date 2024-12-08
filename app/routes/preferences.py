from flask import Blueprint, request, jsonify
from app.models import db, User, MatchingPreference

bp = Blueprint('preferences', __name__, url_prefix='/preferences')

# 매칭 선호도 설정 및 수정
@bp.route('/update', methods=['POST', 'PUT'])
def update_preferences():
    data = request.json
    user_id = data.get('user_id')
    preferred_genders = data.get('preferred_genders')
    min_age = data.get('min_age')
    max_age = data.get('max_age')

    # 입력값 확인
    if not user_id or not preferred_genders or min_age is None or max_age is None:
        return jsonify({"error": "user_id, preferred_genders, min_age, and max_age are required"}), 400

    # 사용자 존재 여부 확인
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 매칭 선호도 조회
    preference = MatchingPreference.query.filter_by(user_id=user_id).first()

    # 선호도 없으면 새로 생성
    if not preference:
        preference = MatchingPreference(
            user_id=user_id,
            preferred_genders=preferred_genders,
            min_age=min_age,
            max_age=max_age
        )
        db.session.add(preference)
    else:
        # 기존 선호도 업데이트
        preference.preferred_genders = preferred_genders
        preference.min_age = min_age
        preference.max_age = max_age

    db.session.commit()

    return jsonify({"message": "Preferences updated successfully"}), 200

# 매칭 선호도 조회
@bp.route('/<int:user_id>', methods=['GET'])
def get_preferences(user_id):
    # 사용자 존재 여부 확인
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 매칭 선호도 조회
    preference = MatchingPreference.query.filter_by(user_id=user_id).first()
    if not preference:
        return jsonify({"error": "No matching preferences found for this user"}), 404

    return jsonify({
        "user_id": preference.user_id,
        "preferred_genders": preference.preferred_genders,
        "min_age": preference.min_age,
        "max_age": preference.max_age
    }), 200