from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, liked_users

bp = Blueprint('likes', __name__, url_prefix='/likes')

# 좋아요 추가
@bp.route('/add/<int:liked_id>', methods=['POST'])
@login_required
def add_like(liked_id):
    # 자신을 좋아요하는 경우 방지
    if current_user.id == liked_id:
        flash("You cannot like yourself.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    # 좋아요할 사용자 존재 여부 확인
    liked_user = User.query.get(liked_id)
    if not liked_user:
        flash("User not found.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    # 이미 좋아요한 사용자인지 확인
    existing_like = db.session.execute(
        liked_users.select().where(liked_users.c.liker_id == current_user.id, liked_users.c.liked_id == liked_id)
    ).fetchone()

    if existing_like:
        flash("You have already liked this user.", "warning")
        return redirect(url_for('profiles.browse_profiles'))

    # 좋아요 추가
    db.session.execute(liked_users.insert().values(liker_id=current_user.id, liked_id=liked_id))
    db.session.commit()

    flash(f"You liked {liked_user.profile.first_name}'s profile.", "success")
    return redirect(url_for('profiles.browse_profiles'))

# 좋아요 취소
@bp.route('/remove/<int:liked_id>', methods=['POST'])
@login_required
def remove_like(liked_id):
    # 좋아요 기록 확인
    existing_like = db.session.execute(
        liked_users.select().where(liked_users.c.liker_id == current_user.id, liked_users.c.liked_id == liked_id)
    ).fetchone()

    if not existing_like:
        flash("You have not liked this user.", "warning")
        return redirect(url_for('likes.liked_users'))

    # 좋아요 삭제
    db.session.execute(
        liked_users.delete().where(liked_users.c.liker_id == current_user.id, liked_users.c.liked_id == liked_id)
    )
    db.session.commit()

    flash("Like removed successfully.", "success")
    return redirect(url_for('likes.liked_users'))

# 좋아요한 사용자 목록 조회
@bp.route('/list', methods=['GET'])
@login_required
def liked_users():
    # 현재 사용자가 좋아요한 사용자 목록 조회
    liked_users = db.session.execute(
        liked_users.select().where(liked_users.c.liker_id == current_user.id)
    ).fetchall()

    # 프로필 데이터를 가져오기
    liked_list = [User.query.get(row.liked_id) for row in liked_users]

    return render_template('likes/liked_users.html', liked_users=liked_list)