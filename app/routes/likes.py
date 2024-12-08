from flask import Blueprint, request, jsonify
from app.models import db, User, likes

bp = Blueprint('likes', __name__, url_prefix='/likes')

# 좋아요 추가
@bp.route('/add', methods=['POST'])
def add_like():
    data = request.json
    liker_id = data.get('liker_id')
    liked_id = data.get('liked_id')

    # 입력값 확인
    if not liker_id or not liked_id:
        return jsonify({"error": "liker_id and liked_id are required"}), 400

    # 자신을 좋아요하는 경우 방지
    if liker_id == liked_id:
        return jsonify({"error": "A user cannot like themselves"}), 400

    # 사용자 존재 여부 확인
    liker = User.query.get(liker_id)
    liked = User.query.get(liked_id)
    if not liker or not liked:
        return jsonify({"error": "One or both users not found"}), 404

    # 이미 좋아요했는지 확인
    existing_like = db.session.execute(
        likes.select().where(likes.c.liker_id == liker_id, likes.c.liked_id == liked_id)
    ).fetchone()

    if existing_like:
        return jsonify({"error": "User already liked"}), 409

    # 좋아요 추가
    db.session.execute(likes.insert().values(liker_id=liker_id, liked_id=liked_id))
    db.session.commit()

    return jsonify({"message": "Like added successfully"}), 201

# 좋아요 취소
@bp.route('/remove', methods=['DELETE'])
def remove_like():
    data = request.json
    liker_id = data.get('liker_id')
    liked_id = data.get('liked_id')

    # 입력값 확인
    if not liker_id or not liked_id:
        return jsonify({"error": "liker_id and liked_id are required"}), 400

    # 좋아요 기록 확인
    existing_like = db.session.execute(
        likes.select().where(likes.c.liker_id == liker_id, likes.c.liked_id == liked_id)
    ).fetchone()

    if not existing_like:
        return jsonify({"error": "Like record not found"}), 404

    # 좋아요 삭제
    db.session.execute(
        likes.delete().where(likes.c.liker_id == liker_id, likes.c.liked_id == liked_id)
    )
    db.session.commit()

    return jsonify({"message": "Like removed successfully"}), 200

# 좋아요한 사용자 목록 조회
@bp.route('/list/<int:user_id>', methods=['GET'])
def get_liked_users(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 사용자가 좋아요한 사용자 목록 조회
    liked_users = db.session.execute(
        likes.select().where(likes.c.liker_id == user_id)
    ).fetchall()

    liked_list = [{"liked_id": row.liked_id} for row in liked_users]

    return jsonify({"liked_users": liked_list}), 200