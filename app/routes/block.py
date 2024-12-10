from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.models import db, User, blocked_users

# 블루프린트 정의
blocks_bp = Blueprint('blocks_bp', __name__, url_prefix='/blocks')

# 사용자 차단
@blocks_bp.route('/block/<int:blocked_id>', methods=['POST'])
@login_required
def block_user(blocked_id):
    if current_user.id == blocked_id:
        flash("You cannot block yourself.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    blocked_user = User.query.get(blocked_id)
    if not blocked_user:
        flash("User not found.", "danger")
        return redirect(url_for('profiles.browse_profiles'))

    # 이미 차단된 사용자인지 확인
    existing_block = db.session.execute(
        blocked_users.select().where(
            blocked_users.c.blocker_id == current_user.id,
            blocked_users.c.blocked_id == blocked_id
        )
    ).fetchone()

    if existing_block:
        flash("You have already blocked this user.", "warning")
    else:
        # 차단 추가
        db.session.execute(
            blocked_users.insert().values(blocker_id=current_user.id, blocked_id=blocked_id)
        )
        db.session.commit()
        flash(f"You blocked {blocked_user.profile.first_name}.", "success")

    return redirect(url_for('profiles.browse_profiles'))

# 차단 취소
@blocks_bp.route('/unblock/<int:blocked_id>', methods=['POST'])
@login_required
def unblock_user(blocked_id):
    # 차단 기록 확인
    existing_block = db.session.execute(
        blocked_users.select().where(
            blocked_users.c.blocker_id == current_user.id,
            blocked_users.c.blocked_id == blocked_id
        )
    ).fetchone()

    if not existing_block:
        flash("You have not blocked this user.", "warning")
        return redirect(url_for('blocks_bp.blocked_users'))

    # 차단 취소
    db.session.execute(
        blocked_users.delete().where(
            blocked_users.c.blocker_id == current_user.id,
            blocked_users.c.blocked_id == blocked_id
        )
    )
    db.session.commit()

    flash("Block removed successfully.", "success")
    return redirect(url_for('blocks_bp.blocked_users'))

# 차단한 사용자 목록 조회
@blocks_bp.route('/list', methods=['GET'])
@login_required
def blocked_users_list():
    # 현재 사용자가 차단한 사용자 목록 조회
    blocked_rows = db.session.execute(
        blocked_users.select().where(blocked_users.c.blocker_id == current_user.id)
    ).fetchall()

    # 차단한 사용자 프로필 데이터 가져오기
    blocked_list = [User.query.get(row.blocked_id) for row in blocked_rows]

    return render_template('blocks.html', blocked_users=blocked_list)